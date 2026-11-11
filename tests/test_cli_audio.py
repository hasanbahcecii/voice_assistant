import sys
from types import SimpleNamespace
import speech_recognition as sr
from settings import Settings
from wake_word import WakeWordDetector
from voice_recognition import VoiceToText
import cli


class Microphone:
    def __init__(self, **_):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass


def test_wake_word_uses_bounded_capture_and_returns_true(monkeypatch):
    monkeypatch.setattr(sr, "Microphone", Microphone)
    detector = WakeWordDetector(device_index=3)
    captured = {}

    def listen(source, **kwargs):
        captured.update(kwargs)
        return "audio"

    monkeypatch.setattr(detector.recognizer, "listen", listen)
    monkeypatch.setattr(detector.recognizer, "recognize_google", lambda *a, **kw: "Hey Assistant!")
    assert detector.ListenForWakeWord() is True
    assert captured["phrase_time_limit"] == 4


def test_timeout_returns_false_and_does_not_loop_forever(monkeypatch):
    monkeypatch.setattr(sr, "Microphone", Microphone)
    detector = WakeWordDetector()

    def timeout(*_, **__):
        raise sr.WaitTimeoutError()

    monkeypatch.setattr(detector.recognizer, "listen", timeout)
    assert detector.ListenForWakeWord() is False


def test_old_command_method_alias_works(monkeypatch):
    monkeypatch.setattr(sr, "Microphone", Microphone)
    listener = VoiceToText()
    monkeypatch.setattr(listener.recognizer, "listen", lambda *a, **kw: "audio")
    monkeypatch.setattr(listener.recognizer, "recognize_google", lambda *a, **kw: "test command")
    assert listener.ListenForCommand() == "test command"


def test_cli_listens_to_command_after_wake_and_tts_failure_does_not_exit(monkeypatch, capsys):
    calls = []
    commands = iter(["Tell me about planets", "exit"])

    class Listener:
        def __init__(self, *_):
            pass

        def AdjustMicrophone(self):
            pass

        def SingleListen(self):
            calls.append("command")
            return next(commands)

    class Wake:
        wake_word = "hey assistant"

        def __init__(self, *_):
            pass

        def MicrophoneSetup(self):
            pass

        def ListenForWakeWord(self):
            calls.append("wake")
            return True

    class TTS:
        def __init__(self, *_):
            pass

        def speak(self, text):
            raise OSError("device unavailable")

    monkeypatch.setattr(Settings, "from_env", lambda: Settings(backend="demo"))
    monkeypatch.setattr(sys, "argv", ["cli.py"])
    monkeypatch.setitem(sys.modules, "voice_recognition", SimpleNamespace(VoiceToText=Listener))
    monkeypatch.setitem(sys.modules, "wake_word", SimpleNamespace(WakeWordDetector=Wake))
    monkeypatch.setitem(sys.modules, "text_to_speech", SimpleNamespace(TextToSpeech=TTS))
    assert cli.main() == 0
    assert calls == ["wake", "command", "wake", "command"]
    assert "Voice output unavailable" in capsys.readouterr().out


def test_missing_credentials_returns_failure_before_audio_setup(monkeypatch, capsys):
    monkeypatch.setattr(Settings, "from_env", lambda: Settings(free_only=False))
    monkeypatch.setattr(sys, "argv", ["voice_assistant_openai.py"])
    assert cli.main("openai") == 1
    assert "OPENAI_API_KEY" in capsys.readouterr().out
