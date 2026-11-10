"""The shared response pipeline; history belongs to a caller's session."""

from contextlib import closing
from dataclasses import dataclass, field
from time import perf_counter
from greetings import Greetings, normalize
from providers import create_provider, ProviderError
from settings import Settings, LANGUAGES


def is_exit_command(text):
    return normalize(text) in {"exit", "quit", "goodbye"} or normalize(text, "tr-TR") in {"çıkış", "kapat", "güle güle"}


@dataclass
class Reply:
    text: str
    source: str
    history: list = field(default_factory=list)
    done: bool = False
    first_token_ms: float = 0
    total_ms: float = 0


class AssistantService:
    def __init__(self, settings=None, provider_factory=create_provider):
        self.settings = settings or Settings.from_env()
        self.provider_factory = provider_factory
        self.greetings = Greetings()

    def stream_reply(self, text, history=None, language=None, backend=None):
        language = language or self.settings.language
        if language not in LANGUAGES:
            raise ValueError("Unsupported language.")
        text = text.strip()
        if not text or len(text) > self.settings.max_input_chars:
            raise ValueError(f"Enter between 1 and {self.settings.max_input_chars} characters.")
        # Whitelist roles and copy input: untrusted browser state cannot add system messages.
        cleaned = [
            dict(role=m["role"], content=m["content"][: self.settings.max_input_chars])
            for m in (history or [])
            if isinstance(m, dict) and m.get("role") in {"user", "assistant"} and isinstance(m.get("content"), str)
        ]
        cleaned = cleaned[-self.settings.history_turns * 2 :]
        started = perf_counter()
        greeting = self.greetings.answer_greeting(text, language)
        if greeting:
            chunks, source = (part for part in (greeting,)), "greeting"
        else:
            provider = self.provider_factory(self.settings, backend)
            prompt = "You are a helpful voice assistant. Give concise, accurate answers in " + (
                "Turkish." if language == "tr-TR" else "English."
            )
            messages = [{"role": "system", "content": prompt}, *cleaned, {"role": "user", "content": text}]
            chunks, source = provider.stream(messages, language), provider.name
        answer, first_token_ms = "", 0.0
        with closing(chunks):
            for chunk in chunks:
                if not chunk:
                    continue
                if not answer:
                    first_token_ms = (perf_counter() - started) * 1000
                answer += chunk
                yield Reply(answer, source, first_token_ms=first_token_ms)
        if not answer.strip():
            raise ProviderError("The model returned an empty response. Please try again.")
        updated = [*cleaned, {"role": "user", "content": text}, {"role": "assistant", "content": answer}]
        yield Reply(
            answer,
            source,
            updated[-self.settings.history_turns * 2 :],
            True,
            first_token_ms,
            (perf_counter() - started) * 1000,
        )

    def respond(self, text, history=None, language=None, backend=None):
        final = None
        for final in self.stream_reply(text, history, language, backend):
            pass
        return final
