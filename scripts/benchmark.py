"""Measure the selected provider, never mix demo and cloud latency figures."""

import argparse
import json
from pathlib import Path
import statistics
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from assistant_service import AssistantService


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=["demo", "openai", "huggingface"], default="demo")
    parser.add_argument("--runs", type=int, default=5)
    args = parser.parse_args()
    if not 1 <= args.runs <= 20:
        parser.error("--runs must be between 1 and 20")
    service = AssistantService()
    replies = [service.respond("What is the capital of Türkiye?", backend=args.backend) for _ in range(args.runs)]
    print(
        json.dumps(
            {
                "backend": args.backend,
                "runs": args.runs,
                "median_first_token_ms": statistics.median(r.first_token_ms for r in replies),
                "median_total_model_ms": statistics.median(r.total_ms for r in replies),
                "includes_stt_tts": False,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
