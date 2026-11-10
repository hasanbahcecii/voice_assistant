import importlib.util
from pathlib import Path
from types import SimpleNamespace
import pytest

spec = importlib.util.spec_from_file_location(
    "deploy_space", Path(__file__).resolve().parents[1] / "scripts/deploy_space.py"
)
deploy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy)


class API:
    def __init__(self, stage="RUNNING"):
        self.stage = stage

    def space_info(self, _):
        return SimpleNamespace(sha="expected")

    def get_space_runtime(self, _):
        return SimpleNamespace(stage=self.stage, raw={"sha": "expected"})


def test_deploy_checks_running_revision_and_demo_api(monkeypatch):
    import gradio_client

    class Client:
        def __init__(self, *_, **__):
            pass

        def predict(self, **kwargs):
            assert kwargs["backend"] == "demo"
            assert kwargs["speak"] is False
            return ("What can you do?", "Demo mode is active", None, "Ready · demo", "timing")

    monkeypatch.setattr(gradio_client, "Client", Client)
    deploy.verify_deployment(API(), "owner/space", "expected", timeout=1)


def test_failed_space_build_fails_deployment():
    with pytest.raises(RuntimeError, match="BUILD_ERROR"):
        deploy.verify_deployment(API("BUILD_ERROR"), "owner/space", "expected", timeout=1)
