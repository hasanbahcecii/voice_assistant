"""Validated configuration shared by the web app and local CLI."""

from dataclasses import dataclass, field
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GOOGLE_STT_ENDPOINT = "https://www.google.com/speech-api/v2/recognize"
LANGUAGES = {"en-US": "en-US-AriaNeural", "tr-TR": "tr-TR-EmelNeural"}


class ConfigurationError(ValueError):
    pass


def usable_key(value):
    return (
        isinstance(value, str) and bool(value.strip()) and not value.lower().startswith(("your", "replace", "example"))
    )


def load_keys(config_path=None):
    """Environment wins. JSON is optional; legacy singular filename is supported."""
    paths = [Path(config_path)] if config_path else [ROOT / "api_keys.json", ROOT / "api_key.json"]
    data = {}
    for path in paths:
        if not path.exists():
            continue
        try:
            current = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ConfigurationError(f"Invalid API configuration: {path.name}") from exc
        if not isinstance(current, dict):
            raise ConfigurationError(f"API configuration must be an object: {path.name}")
        for key, value in current.items():
            if key not in data and usable_key(value):
                data[key] = value.strip()

    def choose(names, json_name):
        for name in names:
            if usable_key(os.getenv(name)):
                return os.environ[name].strip()
        return data.get(json_name, "")

    return {
        "openai_api_key": choose(["OPENAI_API_KEY"], "openai_api_key"),
        "huggingface_api_key": choose(["HF_TOKEN", "HUGGINGFACE_API_KEY"], "huggingface_api_key"),
    }


@dataclass(frozen=True)
class Settings:
    backend: str = "auto"
    language: str = "en-US"
    openai_model: str = "gpt-3.5-turbo"
    hf_model: str = ""
    hf_provider: str = "auto"
    timeout: float = 30.0
    max_tokens: int = 256
    history_turns: int = 8
    max_input_chars: int = 4000
    max_audio_seconds: int = 30
    microphone_index: int | None = None
    wake_engine: str = "google"
    wake_model_path: str = ""
    openai_api_key: str = field(default="", repr=False)
    huggingface_api_key: str = field(default="", repr=False)

    def __post_init__(self):
        if self.backend not in {"auto", "demo", "openai", "huggingface"}:
            raise ConfigurationError("BACKEND must be auto, demo, openai or huggingface.")
        if self.language not in LANGUAGES:
            raise ConfigurationError("ASSISTANT_LANGUAGE must be en-US or tr-TR.")
        if not 1 <= self.timeout <= 120:
            raise ConfigurationError("API_TIMEOUT must be between 1 and 120 seconds.")
        if not 1 <= self.max_tokens <= 2048:
            raise ConfigurationError("MAX_TOKENS must be between 1 and 2048.")
        if not 1 <= self.history_turns <= 32:
            raise ConfigurationError("HISTORY_TURNS must be between 1 and 32.")
        if self.microphone_index is not None and self.microphone_index < 0:
            raise ConfigurationError("MICROPHONE_INDEX cannot be negative.")
        if self.wake_engine not in {"google", "vosk"}:
            raise ConfigurationError("WAKE_ENGINE must be google or vosk.")

    @classmethod
    def from_env(cls, config_path=None):
        try:
            return cls(
                backend=os.getenv("BACKEND", "auto").lower(),
                language=os.getenv("ASSISTANT_LANGUAGE", "en-US"),
                openai_model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                hf_model=os.getenv("HF_MODEL", ""),
                hf_provider=os.getenv("HF_PROVIDER", "auto"),
                timeout=float(os.getenv("API_TIMEOUT", "30")),
                max_tokens=int(os.getenv("MAX_TOKENS", "256")),
                history_turns=int(os.getenv("HISTORY_TURNS", "8")),
                microphone_index=int(os.environ["MICROPHONE_INDEX"]) if os.getenv("MICROPHONE_INDEX") else None,
                wake_engine=os.getenv("WAKE_ENGINE", "google"),
                wake_model_path=os.getenv("WAKE_MODEL_PATH", ""),
                **load_keys(config_path),
            )
        except ConfigurationError:
            raise
        except ValueError as exc:
            raise ConfigurationError("Numeric environment settings are invalid.") from exc

    def resolve_backend(self, selected=None):
        backend = selected or self.backend
        if backend == "auto":
            if self.openai_api_key:
                return "openai"
            if self.huggingface_api_key:
                return "huggingface"
            return "demo"
        if backend not in {"demo", "openai", "huggingface"}:
            raise ConfigurationError("Unknown backend.")
        return backend
