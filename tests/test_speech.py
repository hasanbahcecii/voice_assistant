import asyncio
from pathlib import Path
import wave
import pytest
import edge_tts
import speech_recognition as sr
from speech import synthesize, recognize_file, SpeechError


def test_failed_tts_removes_temporary_file(monkeypatch):
    captured = []

    async def fail(self, path):
        captured.append(path)
        Path(path).write_bytes(b"partial")
        raise RuntimeError("remote failed")

    monkeypatch.setattr(edge_tts.Communicate, "save", fail)
    with pytest.raises(RuntimeError):
        asyncio.run(synthesize("hello"))
    assert captured
    assert not Path(captured[0]).exists()


def test_tts_file_closed_before_external_writer(monkeypatch):
    async def save(self, path):
        with open(path, "wb") as handle:
            handle.write(b"mp3-test")

    monkeypatch.setattr(edge_tts.Communicate, "save", save)
    path = Path(asyncio.run(synthesize("hello")))
    try:
        assert path.read_bytes() == b"mp3-test"
    finally:
        path.unlink()


def test_stt_audio_limit_rejects_before_network(tmp_path, monkeypatch):
    path = tmp_path / "long.wav"
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(8000)
        output.writeframes(b"\0\0" * 16000)

    def fail(*_, **__):
        pytest.fail("Should not call network")

    monkeypatch.setattr(sr.Recognizer, "recognize_google", fail)
    with pytest.raises(SpeechError, match="at most"):
        recognize_file(path, max_seconds=1)


def test_invalid_audio_is_safe(tmp_path):
    path = tmp_path / "bad.wav"
    path.write_text("not audio")
    with pytest.raises(SpeechError):
        recognize_file(path)


def test_stt_uses_https_and_selected_language(tmp_path, monkeypatch):
    path = tmp_path / "short.wav"
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(8000)
        output.writeframes(b"\0\0" * 800)
    captured = {}

    def recognize(self, audio, **kwargs):
        captured.update(kwargs)
        return "merhaba"

    monkeypatch.setattr(sr.Recognizer, "recognize_google", recognize)
    assert recognize_file(path, "tr-TR") == "merhaba"
    assert captured["endpoint"].startswith("https://")
    assert captured["language"] == "tr-TR"
