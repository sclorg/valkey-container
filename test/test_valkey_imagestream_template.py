import pytest

from container_ci_suite.openshift import OpenShiftAPI

from conftest import VARS


class TestValkeyImagestreamTemplate:
    def setup_method(self):
        self.oc_api = OpenShiftAPI(
            pod_name_prefix="valkey", version=VARS.VERSION, shared_cluster=True
        )

    def teardown_method(self):
        self.oc_api.delete_project()

    @pytest.mark.parametrize(
        "template",
        ["valkey-ephemeral-template.json", "valkey-persistent-template.json"],
    )
    def test_valkey_imagestream_template(self, template):
        os_name = "".join(i for i in VARS.OS if not i.isdigit())
        assert self.oc_api.deploy_image_stream_template(
            imagestream_file=f"imagestreams/valkey-{os_name}.json",
            template_file=f"examples/{template}",
            app_name=self.oc_api.pod_name_prefix,
        )
        assert self.oc_api.is_pod_running(pod_name_prefix=self.oc_api.pod_name_prefix)
