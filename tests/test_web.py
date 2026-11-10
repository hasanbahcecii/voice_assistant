import app
from assistant_service import AssistantService
from providers import ProviderError
from settings import Settings
from speech import SpeechError


def test_text_demo_pipeline_runs_without_audio_hardware():
    results = list(
        app.voice_pipeline(None, "What can you do?", backend="demo", speak=False, service=AssistantService(Settings()))
    )
    transcript, answer, audio, status, state, timing = results[-1]
    assert transcript == "What can you do?"
    assert "Demo mode" in answer
    assert audio is None
    assert status == "Ready · demo"
    assert len(state["history"]) == 2
    assert "First token" in timing


def test_tts_failure_preserves_text_and_conversation(monkeypatch):
    def fail(*_):
        raise SpeechError("Voice unavailable")

    monkeypatch.setattr(app, "synthesize_sync", fail)
    result = list(app.voice_pipeline(None, "hello", backend="demo", service=AssistantService(Settings())))[-1]
    assert result[1].startswith("Hello")
    assert result[2] is None
    assert "Voice unavailable" in result[3]
    assert len(result[4]["history"]) == 2


def test_unknown_audio_is_recoverable(monkeypatch):
    def fail(*_):
        raise SpeechError("Could not understand")

    monkeypatch.setattr(app, "recognize_file", fail)
    result = list(app.voice_pipeline("audio.wav", service=AssistantService(Settings())))[-1]
    assert result[3] == "Could not understand"
    assert result[4]["history"] == []


def test_provider_failure_does_not_commit_partial_history():
    class Failing:
        name = "fake"

        def stream(self, *_):
            yield "Partial"
            raise ProviderError("Unavailable")

    service = AssistantService(Settings(), lambda *_: Failing())
    result = list(app.voice_pipeline(None, "question", service=service, speak=False))[-1]
    assert result[1] == "Partial"
    assert result[3] == "Unavailable"
    assert result[4]["history"] == []


def test_changed_language_clears_old_history():
    state = {"language": "en-US", "backend": "demo", "history": [{"role": "user", "content": "old"}]}
    result = list(app.voice_pipeline(None, "merhaba", "tr-TR", "demo", state, False, AssistantService(Settings())))[-1]
    assert all(m["content"] != "old" for m in result[4]["history"])


def test_empty_input_is_recoverable():
    result = list(app.voice_pipeline(None, speak=False, service=AssistantService(Settings())))[-1]
    assert "Record audio" in result[3]


def test_build_gradio_app_without_starting_a_server(monkeypatch):
    monkeypatch.setenv("GRADIO_ANALYTICS_ENABLED", "False")
    demo = app.build_demo()
    assert any(component.get("props", {}).get("label") == "Language" for component in demo.config["components"])


def test_missing_provider_configuration_has_user_message():
    result = list(
        app.voice_pipeline(None, "question", backend="openai", speak=False, service=AssistantService(Settings()))
    )[-1]
    assert "not configured" in result[3]
    assert "OPENAI_API_KEY" not in result[3]
    assert result[4]["history"] == []
