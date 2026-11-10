"""Optional local key-file template. Production uses environment variables."""

import json
import os
from settings import ROOT, load_keys


class APIManager:
    def __init__(self):
        self.config_file = ROOT / "api_keys.json"
        self.api_keys = load_keys()

    def load_api_keys(self):
        self.api_keys = load_keys()
        return self.api_keys

    def create_config_template(self):
        # Exclusive create prevents accidental overwriting of real credentials.
        with self.config_file.open(
            "x", encoding="utf-8", opener=lambda path, flags: os.open(path, flags, 0o600)
        ) as handle:
            json.dump(
                {"openai_api_key": "your_openai_api_key_here", "huggingface_api_key": "your_huggingface_api_key_here"},
                handle,
                indent=2,
            )

    def check_api_keys(self):
        for name, value in self.api_keys.items():
            print(f"{name}: {'set' if value else 'not set'}")


if __name__ == "__main__":
    manager = APIManager()
    if not manager.config_file.exists():
        manager.create_config_template()
    manager.check_api_keys()
