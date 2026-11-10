"""Browser/Spaces entry point: no server microphone or playback dependencies."""

import time
from pathlib import Path
from assistant_service import AssistantService
from providers import ProviderError
from settings import Settings, ConfigurationError
from speech import recognize_file, synthesize_sync, SpeechError


def voice_pipeline(audio, text="", language="en-US", backend="auto", state=None, speak=True, service=None):
    """Stream text first, then audio. State is per Gradio session."""
    started = time.perf_counter()
    state = state or {}
    history = state.get("history", []) if state.get("language") == language and state.get("backend") == backend else []
    new_state = {"history": history, "language": language, "backend": backend}
    transcript = text.strip()
    answer = ""
    try:
        service = service or AssistantService()
        if not transcript:
            if not audio:
                yield "", "", None, "Record audio or enter a message.", new_state, ""
                return
            transcript = recognize_file(audio, language, service.settings.max_audio_seconds, service.settings.timeout)
        stt_ms = (time.perf_counter() - started) * 1000
        final = None
        for reply in service.stream_reply(transcript, history, language, backend):
            answer = reply.text
            if reply.done:
                final = reply
            else:
                yield transcript, answer, None, f"Responding · {reply.source}", new_state, ""
        new_state = {"history": final.history, "language": language, "backend": backend}
        status = f"Ready · {final.source}"
        metrics = (
            f"Input: {stt_ms:.0f} ms · First token: {final.first_token_ms:.0f} ms · Model: {final.total_ms:.0f} ms"
        )
        yield transcript, answer, None, status + (" · Generating audio…" if speak else ""), new_state, metrics
        path = None
        if speak:
            try:
                path = synthesize_sync(answer, language, service.settings.timeout)
            except SpeechError as exc:
                status += f" · {exc}"
        metrics += f" · Total: {(time.perf_counter() - started) * 1000:.0f} ms"
        try:
            yield transcript, answer, path, status, new_state, metrics
        finally:
            # Gradio copies returned audio to its managed cache before advancing.
            if path:
                Path(path).unlink(missing_ok=True)
    except ConfigurationError:
        message = (
            "Seçilen sağlayıcı bu sunucuda yapılandırılmamış. Demo seçeneğini kullanabilir veya uygulama sahibine başvurabilirsin."
            if language == "tr-TR"
            else "The selected provider is not configured on this server. Choose Demo or contact the app owner."
        )
        yield transcript, "", None, message, new_state, ""
    except (ProviderError, SpeechError, ValueError) as exc:
        # Partial streamed answers are not committed to history when the request fails.
        yield transcript, answer, None, str(exc), new_state, ""
    except Exception:
        yield transcript, answer, None, "The request failed. Please try again.", new_state, ""


def build_demo():
    import gradio as gr

    settings = Settings.from_env()
    with gr.Blocks(title="Voice Assistant", delete_cache=(300, 600)) as demo:
        gr.Markdown(
            "# 🎙️ Voice Assistant\nSpeak or type in English or Turkish. Choose a configured provider for real conversations; Demo uses prepared responses."
        )
        gr.Markdown(
            "Audio is sent to Google for transcription and response text to Microsoft Edge TTS when voice output is enabled. Selected model providers receive your messages and recent session history."
        )
        session = gr.State({})
        with gr.Row():
            language = gr.Dropdown(
                [("English", "en-US"), ("Türkçe", "tr-TR")], value=settings.language, label="Language"
            )
            backend = gr.Dropdown(["auto", "demo", "openai", "huggingface"], value=settings.backend, label="Provider")
        audio = gr.Audio(
            sources=["microphone", "upload"],
            type="filepath",
            format="wav",
            label="Record a message (up to 30 seconds)",
        )
        text = gr.Textbox(label="Or type a message", max_lines=5)
        speak = gr.Checkbox(value=True, label="Voice response")
        with gr.Row():
            submit = gr.Button("Send", variant="primary")
            clear = gr.Button("Clear conversation")
        transcript = gr.Textbox(label="You said", interactive=False)
        answer = gr.Textbox(label="Assistant", interactive=False)
        output = gr.Audio(label="Voice response")
        status = gr.Textbox(
            label="Status", value=f"Configured provider: {settings.resolve_backend()}", interactive=False
        )
        metrics = gr.Textbox(label="Timing", interactive=False)
        inputs = [audio, text, language, backend, session, speak]
        outputs = [transcript, answer, output, status, session, metrics]
        send_event = submit.click(voice_pipeline, inputs, outputs, concurrency_limit=1, api_name="respond")
        clear.click(
            lambda: (None, "", "", "", None, "Conversation cleared.", {}, ""),
            outputs=[audio, text, transcript, answer, output, status, session, metrics],
            cancels=[send_event],
            api_name="clear",
        )
        language.change(lambda: {}, outputs=session, cancels=[send_event], api_name=False)
        backend.change(lambda: {}, outputs=session, cancels=[send_event], api_name=False)
    return demo.queue(max_size=20)


if __name__ == "__main__":
    build_demo().launch(max_file_size="10mb")
