import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_space_bundle_is_self_contained_and_has_no_local_secrets(tmp_path):
    files = json.loads((ROOT / "deploy/space-files.json").read_text())
    for name in files:
        shutil.copy2(ROOT / name, tmp_path / name)
    assert not (tmp_path / "api_keys.json").exists()
    assert not (tmp_path / "cli.py").exists()
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            'from app import build_demo; from settings import Settings; from assistant_service import AssistantService; assert AssistantService(Settings()).respond("hello").source == "greeting"; build_demo()',
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr


def test_credentials_are_gitignored():
    for name in ["api_key.json", "api_keys.json", ".env", ".env.local"]:
        result = subprocess.run(["git", "check-ignore", name], cwd=ROOT, capture_output=True)
        assert result.returncode == 0


def test_live_deployment_requires_manual_dispatch():
    import yaml

    workflow = yaml.load((ROOT / ".github/workflows/deploy-space.yml").read_text(), Loader=yaml.BaseLoader)
    assert "workflow_dispatch" in workflow["on"]
    assert "push" not in workflow["on"]
