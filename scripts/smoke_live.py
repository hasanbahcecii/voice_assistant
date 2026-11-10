"""Explicit opt-in real-provider smoke check. Requires server credentials."""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from assistant_service import AssistantService
from speech import recognize_file, synthesize_sync


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True, choices=["openai", "huggingface"])
    parser.add_argument("--audio", type=Path)
    parser.add_argument("--language", default="en-US", choices=["en-US", "tr-TR"])
    args = parser.parse_args()
    service = AssistantService()
    question = "What is the capital of Türkiye?"
    if args.audio:
        question = recognize_file(args.audio, args.language, timeout=service.settings.timeout)
    reply = service.respond(question, language=args.language, backend=args.backend)
    assert reply.source == args.backend and reply.text.strip()
    if args.audio:
        path = Path(synthesize_sync(reply.text, args.language, service.settings.timeout))
        try:
            assert path.stat().st_size > 0
        finally:
            path.unlink(missing_ok=True)
    print(
        f"PASS: {args.backend}; first token {reply.first_token_ms:.0f} ms; completion {reply.total_ms:.0f} ms; audio checked: {bool(args.audio)}"
    )


if __name__ == "__main__":
    main()
