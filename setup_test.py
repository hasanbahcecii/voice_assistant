"""Dependency validation, not a substitute for pytest behavior tests."""

import argparse
import importlib
import sys


def setup_test(local=False):
    modules = ["gradio", "openai", "huggingface_hub", "speech_recognition", "edge_tts"]
    if local:
        modules += ["pyaudio", "pygame"]
    missing = []
    print(f"Python: {sys.version.split()[0]}")
    for name in modules:
        try:
            importlib.import_module(name)
            print(f"{name}: OK")
        except ImportError:
            missing.append(name)
            print(f"{name}: MISSING")
    return 1 if missing else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true")
    raise SystemExit(setup_test(parser.parse_args().local))
