import pytest

from container_ci_suite.container_lib import ContainerTestLib
from container_ci_suite.engines.podman_wrapper import PodmanCLIWrapper

from conftest import VARS

test_app = VARS.TEST_DIR / "test-app"


class TestValkeyApplicationContainer:
    def setup_method(self):
        self.s2i_app = ContainerTestLib(image_name=VARS.IMAGE_NAME, s2i_image=True)

    def teardown_method(self):
        self.s2i_app.cleanup()

    @pytest.mark.parametrize(
        "password,test_name",
        [
            ("pass", "no_root"),
            ("", "no_pass"),
            ("pass", "no_pass_altuid"),
            ("pass", "no_root_altuid"),
        ]
    )
    def test_run_app_test(self, password, test_name):
        """
        Test checks if valkey server works with different settings.
        Like 'No root' user with password, 'w/o password'
        and with different user and password
        """
        container_arg = f"-e VALKEY_PASSWORD={password}" if password != "" else ""
        container_arg = f"{container_arg} -u 12345" if "altuid" in test_name else ""
        assert self.s2i_app.create_container(
            cid_file_name=test_name,
            container_args=f"--user=100001 {container_arg}"
        )
        # assert ContainerImage.wait_for_cid(cid_file_name=test_name)
        cid = self.s2i_app.get_cid(cid_file_name=test_name)
        assert cid
        cip = self.s2i_app.get_cip(cid_file_name=test_name)
        assert cip
        testing_password = f"-a {password}" if password != "" else ""
        valkey_cmd = f"valkey-cli -h {cip} {testing_password}"
        # Test with valkey-cli returns 'PONG' from the different container
        valkey_output = PodmanCLIWrapper.podman_run_command_and_remove(
            cid_file_name=VARS.IMAGE_NAME,
            cmd=f"{valkey_cmd} ping",
            return_output=True
        )
        assert "PONG" in valkey_output, f"The command {valkey_cmd} should return PONG"
        # The password '_foo' has to fail. It was not initiated
        valkey_output = PodmanCLIWrapper.podman_run_command_and_remove(
            cid_file_name=VARS.IMAGE_NAME,
            cmd=f"{valkey_cmd}_foo ping",
            return_output=False
        )
        assert valkey_output == 0, "The command -e VALKEY_PASSWORD=\"pass_foo\" has to fail"
        # The valkey-cli should return PONG from the running container
        valkey_output = PodmanCLIWrapper.podman_exec_shell_command(
            cid_file_name=cid,
            cmd=f"{valkey_cmd} ping"
        )
        assert "PONG" in valkey_output, "Local access FAILED"
        # The valkey-cli set value 'a' to 1
        assert PodmanCLIWrapper.podman_exec_shell_command(
            cid_file_name=cid,
            cmd=f"{valkey_cmd} set a 1",
            return_output=False
        ) == 0
        # The valkey-cli set value '2' to 2
        assert PodmanCLIWrapper.podman_exec_shell_command(
            cid_file_name=cid,
            cmd=f"{valkey_cmd} set b 2",
            return_output=False
        ) == 0
        # Checks if value b is set to '2'
        valkey_get_value = PodmanCLIWrapper.podman_exec_shell_command(
            cid_file_name=cid,
            cmd=f"{valkey_cmd} get b 2>/dev/null"
        ).strip()
        assert int(valkey_get_value) == 2

    @pytest.mark.parametrize(
        "bind_address",
        [
            "",
            "-e BIND_ADDRESS=127.0.0.1",
        ]
    )
    def test_bind_address(self, bind_address):
        """
        Test checks if BIND_ADDRESS works properly.
        In case it is not set, then checks if valkey-cli returns PONG.
        In case it is set, then checks if configuration file is really changed.
        """
        cid_file_name = "bind_address"
        assert self.s2i_app.create_container(
            cid_file_name=cid_file_name,
            container_args=f"--user=100001 -e VALKEY_PASSWORD=pass {bind_address}"
        )
        cid = self.s2i_app.get_cid(cid_file_name=cid_file_name)
        assert cid
        cip = self.s2i_app.get_cip(cid_file_name=cid_file_name)
        assert cip
        assert PodmanCLIWrapper.podman_exec_shell_command(
            cid_file_name=cid,
            cmd="test -f ${VALKEY_CONF}",
            return_output=False
        ) == 0
        if bind_address:
            assert PodmanCLIWrapper.podman_exec_shell_command(
                cid_file_name=cid,
                cmd="grep \"^bind 127.0.0.1\" ${VALKEY_CONF}",
                return_output=False
            ) == 0
            # Quit test suite. valkey container will not response. bind is set to localhost
        else:
            # Check that VALKEY_CONF really does contain 'bind 127.0.0.1'
            assert not PodmanCLIWrapper.podman_exec_shell_command(
                cid_file_name=cid,
                cmd="grep \"^bind 127.0.0.1\" ${VALKEY_CONF}",
                return_output=False
            )
            # Checks if valkey-cli returns PONG
            valkey_return_value = PodmanCLIWrapper.podman_run_command_and_remove(
                cid_file_name=VARS.IMAGE_NAME,
                cmd=f"valkey-cli -h {cip} -a pass ping"
            ).strip()
            assert "PONG" in valkey_return_value, f"valkey-cli -h {cip} -a pass ping has to return PONG"
