"""Shared CPU-only GGUF runtime. Weights are downloaded once, without an API key."""

from contextlib import contextmanager
from functools import lru_cache
from threading import Lock
import time

from providers import ProviderError

_LOAD_LOCK = Lock()
_GENERATE_LOCK = Lock()


@lru_cache(maxsize=1)
def _load_model(repo, filename, revision, threads):
    from huggingface_hub import hf_hub_download
    from llama_cpp import Llama

    path = hf_hub_download(repo_id=repo, filename=filename, revision=revision, token=False)
    return Llama(
        model_path=path,
        n_ctx=4096,
        n_batch=256,
        n_threads=threads,
        n_threads_batch=threads,
        n_gpu_layers=0,
        verbose=False,
        seed=42,
    )


def get_model(settings):
    # lru_cache alone can initialize the same model twice on concurrent cold requests.
    with _LOAD_LOCK:
        return _load_model(
            settings.local_model_repo, settings.local_model_file, settings.local_model_revision, settings.local_threads
        )


def make_prompt(messages, model_format="chatml", thinking_prefill=False):
    if model_format == "gemma":
        # Gemma merges system instructions into the first user turn.
        system = ""
        parts = []
        for message in messages:
            content = message["content"]
            for token in ("<start_of_turn>", "<end_of_turn>", "<bos>", "<eos>"):
                content = content.replace(token, token.replace("<", "< ").replace(">", " >"))
            if message["role"] == "system":
                system += content + "\n\n"
                continue
            if message["role"] == "user" and system:
                content, system = system + content, ""
            role = "model" if message["role"] == "assistant" else "user"
            parts.append(f"<start_of_turn>{role}\n{content}<end_of_turn>\n")
        # llama.cpp adds Gemma's BOS token using model metadata.
        return "".join(parts) + "<start_of_turn>model\n"
    # Escape model control tokens in browser input/history.
    parts = []
    for message in messages:
        content = message["content"].replace("<|", "< |").replace("|>", "| >")
        parts.append(f"<|im_start|>{message['role']}\n{content}<|im_end|>\n")
    # Instruct-2507 is a non-thinking model; use its plain ChatML generation prefix.
    suffix = "<think>\n\n</think>\n\n" if thinking_prefill else ""
    return "".join(parts) + "<|im_start|>assistant\n" + suffix


@contextmanager
def model_session(settings):
    if not _GENERATE_LOCK.acquire(timeout=settings.timeout):
        raise ProviderError("The local model is busy. Please try again shortly.")
    try:
        yield get_model(settings)
    finally:
        _GENERATE_LOCK.release()


def stream_local(settings, messages):
    try:
        with model_session(settings) as model:
            messages = list(messages)
            budget = model.n_ctx() - settings.max_tokens - 8
            prompt = make_prompt(messages, settings.local_model_format, settings.local_thinking_prefill)
            while len(model.tokenize(prompt.encode(), add_bos=True)) > budget:
                if len(messages) <= 2:
                    raise ProviderError("Message is too long for the local model. Please shorten it.")
                # Even malformed odd-length browser history must preserve the newest user message.
                del messages[1 : min(3, len(messages) - 1)]
                prompt = make_prompt(messages, settings.local_model_format, settings.local_thinking_prefill)
            started = time.monotonic()
            stream = model.create_completion(
                prompt=prompt,
                max_tokens=settings.max_tokens,
                temperature=0.0,
                top_p=0.8,
                top_k=20,
                repeat_penalty=1.0,
                min_p=0.0,
                stop=["<|im_end|>", "<|im_start|>", "<end_of_turn>", "<eos>"],
                stream=True,
            )
            try:
                for chunk in stream:
                    if time.monotonic() - started > settings.timeout:
                        raise ProviderError("The local model timed out. Please try a shorter question.")
                    text = chunk["choices"][0].get("text", "")
                    if text:
                        yield text
            finally:
                stream.close()
    except ProviderError:
        raise
    except Exception as exc:
        raise ProviderError("The local model could not run. Please retry after the model download finishes.") from exc
