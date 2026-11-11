"""One CLI loop shared by both providers; --text needs no audio hardware."""

import argparse
import time
from assistant_service import AssistantService, is_exit_command
from providers import create_provider, ProviderError
from settings import Settings, ConfigurationError
from speech import SpeechError


def main(backend=None, text_only=False):
    parser = argparse.ArgumentParser(description="Voice Assistant")
    parser.add_argument(
        "--text", action="store_true", default=text_only, help="Use the keyboard; no microphone or TTS required"
    )
    parser.add_argument("--backend", choices=["auto", "local", "demo", "openai", "huggingface"], default=backend)
    parser.add_argument("--language", choices=["en-US", "tr-TR"])
    parser.add_argument("--microphone", type=int)
    args = parser.parse_args()
    try:
        settings = Settings.from_env()
        selected = settings.resolve_backend(args.backend)
        create_provider(settings, selected)  # validate before probing any audio hardware
        language = args.language or settings.language
        service = AssistantService(settings)
        history = []
        listener = wake = tts = None
        if not args.text:
            from voice_recognition import VoiceToText
            from wake_word import WakeWordDetector
            from text_to_speech import TextToSpeech

            device = args.microphone if args.microphone is not None else settings.microphone_index
            listener = VoiceToText(device, language, settings.timeout)
            wake = WakeWordDetector(device, language, settings.wake_engine, settings.wake_model_path, settings.timeout)
            tts = TextToSpeech(language, settings.timeout)
            listener.AdjustMicrophone()
            wake.MicrophoneSetup()
            print(f"Say '{wake.wake_word}', pause, then speak your command.")
        print(f"Backend: {selected} | Language: {language} | exit / çıkış: quit")
        while True:
            try:
                if args.text:
                    command = input("> ")
                else:
                    if not wake.ListenForWakeWord():
                        continue
                    print("Listening for command…")
                    command = listener.SingleListen()
                if not command:
                    continue
                if is_exit_command(command):
                    break
                reply = None
                printed = 0
                for reply in service.stream_reply(command, history, language, selected):
                    if not reply.done:
                        if not printed:
                            print(f"[{reply.source}] ", end="", flush=True)
                        print(reply.text[printed:], end="", flush=True)
                        printed = len(reply.text)
                print()
                history = reply.history
                print(f"First token: {reply.first_token_ms:.0f} ms | Response: {reply.total_ms:.0f} ms")
                if tts:
                    try:
                        tts.speak(reply.text)
                    except Exception:
                        print("Voice output unavailable; use the text response above.")
            except (ProviderError, SpeechError, ValueError) as exc:
                print(str(exc))
                if not args.text:
                    time.sleep(1)
    except (KeyboardInterrupt, EOFError):
        print("Goodbye!")
    except (ConfigurationError, OSError, ImportError) as exc:
        print(f"Startup failed: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
