import json
from types import SimpleNamespace
import httpx
import openai
import pytest
from providers import OpenAIProvider, HuggingFaceProvider, ProviderError
from settings import Settings


def test_openai_stream_uses_installed_sdk_and_real_request_contract(monkeypatch):
    captured = {}

    def handle(request):
        captured.update(json.loads(request.content))
        body = (
            "data: "
            + json.dumps(
                {
                    "id": "test",
                    "object": "chat.completion.chunk",
                    "created": 0,
                    "model": "gpt-3.5-turbo",
                    "choices": [{"index": 0, "delta": {"content": "Ankara"}, "finish_reason": None}],
                }
            )
            + "\n\ndata: [DONE]\n\n"
        )
        return httpx.Response(200, text=body, headers={"content-type": "text/event-stream"})

    real_client = openai.OpenAI
    monkeypatch.setattr(
        openai,
        "OpenAI",
        lambda **kw: real_client(**kw, http_client=httpx.Client(transport=httpx.MockTransport(handle))),
    )
    provider = OpenAIProvider(Settings(openai_api_key="fake-test-key"))
    assert list(provider.stream([{"role": "user", "content": "capital?"}], "en-US")) == ["Ankara"]
    assert captured["stream"] is True
    assert captured["model"] == "gpt-3.5-turbo"
    assert captured["max_tokens"] == 256


def test_openai_authentication_error_does_not_expose_raw_response(monkeypatch):
    real_client = openai.OpenAI
    transport = httpx.MockTransport(
        lambda _: httpx.Response(401, json={"error": {"message": "secret-provider-detail"}})
    )
    monkeypatch.setattr(openai, "OpenAI", lambda **kw: real_client(**kw, http_client=httpx.Client(transport=transport)))
    with pytest.raises(ProviderError) as error:
        list(OpenAIProvider(Settings(openai_api_key="fake-test-key")).stream([], "en-US"))
    assert "authentication" in str(error.value)
    assert "secret-provider-detail" not in str(error.value)


def test_huggingface_chat_contract_and_stream(monkeypatch):
    import huggingface_hub

    captured = {}

    class Client:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def chat_completion(self, **kwargs):
            captured.update(kwargs)
            yield SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="Merhaba"))])

    monkeypatch.setattr(huggingface_hub, "InferenceClient", Client)
    provider = HuggingFaceProvider(Settings(huggingface_api_key="fake-test-token", hf_model="test/model"))
    assert list(provider.stream([{"role": "user", "content": "selam"}], "tr-TR")) == ["Merhaba"]
    assert captured["model"] == "test/model"
    assert captured["stream"] is True
