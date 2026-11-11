"""Measure a downloaded GGUF on CPU; inspect answers as well as timings."""

import argparse
import json
from pathlib import Path
import resource
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from local_model import make_prompt  # noqa: E402

CASES = [
    ("capital", "tr-TR", "Türkiye’nin başkenti neresidir? Tek cümleyle yanıtla."),
    ("math", "tr-TR", "Bir kitap 45 TL. Üç kitap alıp 200 TL verirsem kaç TL para üstü alırım?"),
    ("instruction", "tr-TR", "Yalnızca üç madde halinde, su tasarrufu için üç öneri yaz. Türkçe yanıtla."),
    ("science", "tr-TR", "Mevsimler neden oluşur? İki kısa cümleyle Türkçe açıkla."),
    ("english", "en-US", "Explain why we wash our hands in one short sentence."),
    ("unknown", "tr-TR", "Benim evimin adresi nedir? Bilmiyorsan açıkça söyle."),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("model", type=Path, help="Downloaded GGUF path")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--thinking-model", action="store_true", help="Earlier Qwen3: prefill empty thinking block")
    parser.add_argument("--qwen35", action="store_true", help="Use Qwen3.5 recommended non-thinking text sampling")
    parser.add_argument(
        "--stable",
        action="store_true",
        help="Lower temperature and disable presence penalty for short multilingual replies",
    )
    parser.add_argument("--gemma", action="store_true", help="Use Gemma chat template and stop tokens")
    args = parser.parse_args()
    from llama_cpp import Llama

    model = Llama(
        model_path=str(args.model),
        n_ctx=4096,
        n_batch=256,
        n_threads=2,
        n_threads_batch=2,
        n_gpu_layers=0,
        verbose=False,
        seed=42,
    )
    results = []
    for name, language, question in CASES:
        prompt = make_prompt(
            [
                {
                    "role": "system",
                    "content": "You are a helpful voice assistant. Give concise, accurate answers in "
                    + ("Turkish." if language == "tr-TR" else "English."),
                },
                {"role": "user", "content": question},
            ],
            model_format="gemma" if args.gemma else "chatml",
        )
        if args.thinking_model or args.qwen35:
            prompt += "<think>\n\n</think>\n\n"
        model.set_seed(42)
        started, first, answer, chunks = time.perf_counter(), None, "", 0
        for chunk in model.create_completion(
            prompt=prompt,
            max_tokens=160,
            temperature=0.2 if args.stable else (1.0 if args.qwen35 else 0.6),
            top_p=0.8 if args.stable else (1.0 if args.qwen35 else 0.95),
            top_k=20,
            repeat_penalty=1.0 if args.qwen35 or args.stable else 1.1,
            min_p=0.0,
            presence_penalty=2.0 if args.qwen35 and not args.stable else 0.0,
            stop=["<|im_end|>", "<|im_start|>", "<end_of_turn>", "<eos>"],
            stream=True,
        ):
            text = chunk["choices"][0]["text"]
            if text and first is None:
                first = time.perf_counter() - started
            answer += text
            chunks += 1
        item = dict(
            case=name,
            language=language,
            prompt=question,
            answer=answer,
            first_token_s=first,
            total_s=time.perf_counter() - started,
            chunks=chunks,
        )
        results.append(item)
        print(json.dumps(item, ensure_ascii=False), flush=True)
        args.output.write_text(
            json.dumps(
                {
                    "model": args.model.name,
                    "threads": 2,
                    "context": 4096,
                    "max_output_tokens": 160,
                    "thinking_prefill": args.thinking_model or args.qwen35,
                    "qwen35_sampling": args.qwen35,
                    "stable_sampling": args.stable,
                    "gemma_template": args.gemma,
                    "max_rss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
                    "results": results,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
