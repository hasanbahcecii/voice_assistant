import pytest


@pytest.fixture(autouse=True)
def isolated_runtime(monkeypatch):
    monkeypatch.setenv("GRADIO_ANALYTICS_ENABLED", "False")
    for key in [
        "OPENAI_API_KEY",
        "HF_TOKEN",
        "HUGGINGFACE_API_KEY",
        "HF_MODEL",
        "HF_PROVIDER",
        "BACKEND",
        "ASSISTANT_LANGUAGE",
        "OPENAI_MODEL",
        "API_TIMEOUT",
        "MAX_TOKENS",
        "HISTORY_TURNS",
        "MICROPHONE_INDEX",
        "WAKE_ENGINE",
        "WAKE_MODEL_PATH",
    ]:
        monkeypatch.delenv(key, raising=False)
