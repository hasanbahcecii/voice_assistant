"""Compatibility entry point for hosted Hugging Face chat inference."""

from openai_apikey_model import AIModel as BaseModel


class AIModel(BaseModel):
    backend = "huggingface"

    def __init__(self):
        super().__init__()
        self.api_key_loaded = bool(self.settings.huggingface_api_key and self.settings.hf_model)


if __name__ == "__main__":
    from cli import main

    raise SystemExit(main("huggingface", text_only=True))
