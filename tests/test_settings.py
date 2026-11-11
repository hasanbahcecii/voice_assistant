import json
import pytest
from settings import Settings, ConfigurationError, load_keys
from providers import create_provider


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    for key in [
        "OPENAI_API_KEY",
        "HF_TOKEN",
        "HUGGINGFACE_API_KEY",
        "BACKEND",
        "ASSISTANT_LANGUAGE",
        "HF_MODEL",
        "API_TIMEOUT",
        "MICROPHONE_INDEX",
    ]:
        monkeypatch.delenv(key, raising=False)


def test_environment_keys_win_and_do_not_leak_in_repr(tmp_path, monkeypatch):
    path = tmp_path / "api_keys.json"
    path.write_text(json.dumps({"openai_api_key": "file-key", "huggingface_api_key": "file-hf"}))
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    settings = Settings.from_env(path)
    assert settings.openai_api_key == "env-key"
    assert settings.huggingface_api_key == "file-hf"
    assert "env-key" not in repr(settings)
    assert "file-hf" not in repr(settings)


def test_placeholder_never_selects_paid_provider(tmp_path):
    path = tmp_path / "keys.json"
    path.write_text(json.dumps({"openai_api_key": "your_openai_api_key_here"}))
    assert Settings.from_env(path).resolve_backend() == "local"


@pytest.mark.parametrize("value", ["[]", "bad json"])
def test_malformed_key_file_reports_configuration_error(tmp_path, value):
    path = tmp_path / "keys.json"
    path.write_text(value)
    with pytest.raises(ConfigurationError):
        load_keys(path)


def test_missing_optional_file_is_valid(tmp_path):
    assert load_keys(tmp_path / "absent.json") == {"openai_api_key": "", "huggingface_api_key": ""}


@pytest.mark.parametrize("kwargs", [{"timeout": 0}, {"language": "xx"}, {"history_turns": 0}, {"microphone_index": -1}])
def test_invalid_settings(kwargs):
    with pytest.raises(ConfigurationError):
        Settings(**kwargs)


def test_selected_cloud_provider_requires_credentials():
    with pytest.raises(ConfigurationError, match="OPENAI_API_KEY"):
        create_provider(Settings(free_only=False), "openai")
    with pytest.raises(ConfigurationError, match="HF_MODEL"):
        create_provider(Settings(free_only=False, huggingface_api_key="fake"), "huggingface")
