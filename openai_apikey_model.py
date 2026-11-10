"""Compatibility entry point for the OpenAI text assistant."""

from assistant_service import AssistantService
from settings import Settings


class AIModel:
    backend = "openai"

    def __init__(self):
        self.settings = Settings.from_env()
        self.service = AssistantService(self.settings)
        self.history = []
        self.api_key_loaded = bool(self.settings.openai_api_key)

    def generate_response(self, question):
        reply = self.service.respond(question, self.history, backend=self.backend)
        self.history = reply.history
        return reply.text, reply.source


if __name__ == "__main__":
    from cli import main

    raise SystemExit(main("openai", text_only=True))
