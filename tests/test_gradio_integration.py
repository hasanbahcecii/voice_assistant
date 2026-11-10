"""Exercise Gradio preprocessing, session state and audio cache, not just callbacks."""

import asyncio
from pathlib import Path
import wave

from gradio.state_holder import SessionState
import app
from assistant_service import AssistantService
from settings import Settings


async def call(demo, state, text="", speak=False, endpoint="respond"):
    index = next(key for key, fn in demo.fns.items() if fn.api_name == endpoint)
    inputs = [None, text, "en-US", "demo", None, speak] if endpoint == "respond" else []
    events, iterator = [], None
    while True:
        result = await asyncio.wait_for(demo.process_api(index, inputs, state=state, iterator=iterator), timeout=10)
        events.append(result["data"])
        if not result["is_generating"]:
            return events
        iterator = result["iterator"]


def test_gradio_sessions_and_clear_are_isolated(monkeypatch):
    class Provider:
        name = "fake"

        def stream(self, messages, language):
            yield f"Prior messages: {len(messages) - 2}"

    service = AssistantService(Settings(), lambda *_: Provider())
    monkeypatch.setattr(app, "AssistantService", lambda: service)
    demo = app.build_demo()

    async def scenario():
        first, second = SessionState(demo), SessionState(demo)
        a = await call(demo, first, "first question")
        b = await call(demo, first, "second question")
        c = await call(demo, second, "independent question")
        assert any(row[1] == "Prior messages: 0" for row in a)
        assert any(row[1] == "Prior messages: 2" for row in b)
        assert any(row[1] == "Prior messages: 0" for row in c)
        await call(demo, first, endpoint="clear")
        cleared = await call(demo, first, "after clear")
        assert any(row[1] == "Prior messages: 0" for row in cleared)

    asyncio.run(scenario())


def test_audio_survives_gradio_postprocessing_after_original_is_deleted(tmp_path, monkeypatch):
    original = tmp_path / "speech.wav"

    def synthesize(*_):
        with wave.open(str(original), "wb") as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(16000)
            output.writeframes(b"\0\0" * 1600)
        return str(original)

    monkeypatch.setattr(app, "synthesize_sync", synthesize)
    demo = app.build_demo()
    events = asyncio.run(call(demo, SessionState(demo), "hello", speak=True))
    audio = next(row[2] for row in events if isinstance(row[2], dict) and row[2].get("path"))
    cached = Path(audio["path"])
    try:
        assert cached.exists()
        assert cached.stat().st_size > 0
        assert not original.exists()
    finally:
        cached.unlink(missing_ok=True)
