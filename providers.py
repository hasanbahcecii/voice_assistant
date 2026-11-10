"""Lazy, streaming model adapters. No microphone or model downloads on import."""

from settings import ConfigurationError


class ProviderError(RuntimeError):
    """Safe for display; never include credentials or raw provider responses."""


class DemoProvider:
    name = "demo"

    def stream(self, messages, language):
        if language == "tr-TR":
            yield "Demo modu etkin. Gerçek sohbet için bir OpenAI veya Hugging Face sağlayıcısı yapılandırın."
        else:
            yield "Demo mode is active. Configure an OpenAI or Hugging Face provider for real conversations."


class OpenAIProvider:
    name = "openai"

    def __init__(self, settings):
        if not settings.openai_api_key:
            raise ConfigurationError("Set OPENAI_API_KEY to use OpenAI.")
        self.settings = settings

    def stream(self, messages, language):
        from openai import OpenAI, AuthenticationError, RateLimitError, APITimeoutError, APIError

        try:
            with OpenAI(api_key=self.settings.openai_api_key, timeout=self.settings.timeout, max_retries=1) as client:
                with client.chat.completions.create(
                    model=self.settings.openai_model,
                    messages=messages,
                    max_tokens=self.settings.max_tokens,
                    stream=True,
                ) as stream:
                    for chunk in stream:
                        if chunk.choices:
                            text = chunk.choices[0].delta.content
                            if text:
                                yield text
        except AuthenticationError as exc:
            raise ProviderError("OpenAI authentication failed. Check the server API key.") from exc
        except RateLimitError as exc:
            raise ProviderError("OpenAI quota or rate limit reached. Try again later.") from exc
        except APITimeoutError as exc:
            raise ProviderError("OpenAI timed out. Please try again.") from exc
        except APIError as exc:
            raise ProviderError("OpenAI is unavailable. Check the model and connection.") from exc


class HuggingFaceProvider:
    name = "huggingface"

    def __init__(self, settings):
        if not settings.huggingface_api_key:
            raise ConfigurationError("Set HF_TOKEN to use Hugging Face inference.")
        if not settings.hf_model:
            raise ConfigurationError("Set HF_MODEL to a chat model supported by your inference provider.")
        self.settings = settings

    def stream(self, messages, language):
        from huggingface_hub import InferenceClient

        try:
            with InferenceClient(
                api_key=self.settings.huggingface_api_key,
                provider=self.settings.hf_provider,
                timeout=self.settings.timeout,
            ) as client:
                for chunk in client.chat_completion(
                    model=self.settings.hf_model,
                    messages=messages,
                    max_tokens=self.settings.max_tokens,
                    stream=True,
                ):
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
        except Exception as exc:
            raise ProviderError(
                "Hugging Face inference failed. Check HF_TOKEN, HF_MODEL, provider access and quota."
            ) from exc


def create_provider(settings, selected=None):
    name = settings.resolve_backend(selected)
    return (
        {"demo": DemoProvider, "openai": OpenAIProvider, "huggingface": HuggingFaceProvider}[name](settings)
        if name != "demo"
        else DemoProvider()
    )
