"""Match a complete greeting, never a substring of a real question."""

import json
import re
from settings import ROOT


def normalize(text, language="en-US"):
    if language == "tr-TR":
        text = text.replace("I", "ı").replace("İ", "i")
    return " ".join(re.findall(r"[^\W_]+", text.casefold(), re.UNICODE))


class Greetings:
    def __init__(self, path=None):
        self.greetings_file = path or ROOT / "greetings.json"
        try:
            with open(self.greetings_file, encoding="utf-8") as source:
                data = json.load(source)
            self.greetings = {
                normalize(key): replies
                for key, replies in data.items()
                if isinstance(replies, list) and replies and all(isinstance(x, str) for x in replies)
            }
        except (OSError, ValueError, AttributeError):
            self.greetings = {"hello": ["Hello! How can I help?"], "hi": ["Hi! How can I help?"]}

    def answer_greeting(self, text, language="en-US"):
        phrase = normalize(text, language)
        if language == "tr-TR":
            return {
                "merhaba": "Merhaba! Nasıl yardımcı olabilirim?",
                "selam": "Selam! Nasıl yardımcı olabilirim?",
                "günaydın": "Günaydın! Nasıl yardımcı olabilirim?",
            }.get(phrase)
        aliases = {
            "good morning": "morning",
            "good afternoon": "afternoon",
            "good evening": "evening",
            "good night": "night",
        }
        replies = self.greetings.get(aliases.get(phrase, phrase))
        return replies[0] if replies else None
