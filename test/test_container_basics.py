import pytest
import subprocess
import tempfile

from container_ci_suite.container_lib import ContainerTestLib
from container_ci_suite.utils import ContainerTestLibUtils
from container_ci_suite.engines.podman_wrapper import PodmanCLIWrapper

from conftest import VARS


class TestValkeyBasicsContainer:

    def setup_method(self):
        self.app = ContainerTestLib(image_name=VARS.IMAGE_NAME, s2i_image=True)

    def teardown_method(self):
        self.app.cleanup()

    def test_check_proper_version(self):
        """
        Function checks if valkey-server returns proper
        VERSION number
        """
        assert VARS.VERSION in PodmanCLIWrapper.podman_run_command_and_remove(
            cid_file_name=VARS.IMAGE_NAME,
            cmd="valkey-server --version"
        )

    def test_invalid_combination(self):
        """
        Function checks if running container with wrong PASSWORD
        with spaces in the VALKEY_PASSWORD really fails
        It should fail. If it doesn't fail,

        """
        with pytest.raises(subprocess.CalledProcessError):
            PodmanCLIWrapper.call_podman_command(
                cmd=f"run --rm -e VALKEY_PASSWORD=\"pass with space\" {VARS.IMAGE_NAME}",
                return_output=False
            )
            #assert not result, "The command -e VALKEY_PASSWORD=\"pass with space\" has to fail"

    def test_run_change_password(self):
        """
        Function checks if setting two different password
        works properly in the container.
        The datadir is shared and mounted to container
        """
        data_dir = tempfile.mkdtemp(prefix="/tmp/valkey-test_log_dir")
        ContainerTestLibUtils.commands_to_run(
            commands_to_run=[
                f"mkdir -p {data_dir}/data",
                f"chown -R 1001:1001 {data_dir}",
                f"chcon -Rvt svirt_sandbox_file_t {data_dir}/"
            ]
        )
        cid_file_name = "testapp1"
        # Create Valkey container with persistent volume and set the initial password
        assert self.app.create_container(
            cid_file_name=cid_file_name,
            container_args=f"-e VALKEY_PASSWORD=foo -v {data_dir}/data:/var/lib/valkey/data:Z"
        )
        cid1 = self.app.get_cid(cid_file_name=cid_file_name)
        cip1 = self.app.get_cip(cid_file_name=cid_file_name)
        assert cip1
        # The valkey-cli command should response with 'PONG'
        valkey_output = PodmanCLIWrapper.podman_run_command_and_remove(
            cid_file_name=VARS.IMAGE_NAME,
            cmd=f"valkey-cli -h {cip1} -a foo ping",
        ).strip()
        assert "PONG" in valkey_output, "Expected return value is 'PONG'"
        PodmanCLIWrapper.call_podman_command(f"stop {cid1} >/dev/null")

        cid_file_name = "testapp2"
        # Create Valkey container with persistent volume and set second initial password
        assert self.app.create_container(
            cid_file_name=cid_file_name,
            container_args=f"-e VALKEY_PASSWORD=bar -v {data_dir}/data:/var/lib/valkey/data:Z"
        )
        cid2 = self.app.get_cid(cid_file_name=cid_file_name)
        cip2 = self.app.get_cip(cid_file_name=cid_file_name)
        assert cip2
        # The valkey-cli command should responds with 'PONG'
        valkey_output = PodmanCLIWrapper.podman_run_command_and_remove(
            cid_file_name=VARS.IMAGE_NAME,
            cmd=f"valkey-cli -h {cip2} -a bar ping"
        ).strip()
        assert "PONG" in valkey_output, "Expected return value is 'PONG'"
        # The old password should not work anymore
        assert PodmanCLIWrapper.podman_run_command_and_remove(
            cid_file_name=VARS.IMAGE_NAME,
            cmd=f"valkey-cli -h {cip2} -a foo ping",
            return_output=False
        ) == 0, "The command with pass -a foo has to fail"
        assert "PONG" in valkey_output, "Expected return value is 'PONG'"
        PodmanCLIWrapper.call_podman_command(f"stop {cid2} >/dev/null")
