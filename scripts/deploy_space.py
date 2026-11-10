"""Upload a tested, allowlisted bundle. Never copy a working directory wholesale."""

import argparse
import json
import os
from pathlib import Path
import shutil
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]


def bundle(destination):
    files = json.loads((ROOT / "deploy/space-files.json").read_text())
    for name in files:
        source = ROOT / name
        if not source.is_file() or source.resolve().parent != ROOT:
            raise ValueError(f"Invalid deployment file: {name}")
        shutil.copy2(source, destination / name)
    return files


def verify_deployment(api, space_id, revision, timeout=600):
    from gradio_client import Client

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        info = api.space_info(space_id)
        runtime = api.get_space_runtime(space_id)
        running_revision = runtime.raw.get("sha")
        stage = str(runtime.stage)
        if info.sha == revision:
            if stage in {"BUILD_ERROR", "RUNTIME_ERROR", "CONFIG_ERROR"}:
                raise RuntimeError(f"Space failed to start: {stage}")
            if stage == "RUNNING" and running_revision == revision:
                result = Client(
                    space_id,
                    token=getattr(api, "token", None),
                    verbose=False,
                    analytics_enabled=False,
                    httpx_kwargs={"timeout": 30},
                ).predict(
                    audio=None,
                    text="What can you do?",
                    language="en-US",
                    backend="demo",
                    speak=False,
                    api_name="/respond",
                )
                # Gradio state is server-managed and excluded from API outputs.
                if "Demo mode" not in result[1] or result[3] != "Ready · demo":
                    raise RuntimeError("Space is running but its demo API smoke test failed.")
                print("Verified deployed revision is RUNNING and demo API passed.")
                return
        time.sleep(5)
    raise TimeoutError("Space did not reach the expected running revision within 10 minutes.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--space", default="hasanbahceci/voice-assistant")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as directory:
        destination = Path(directory)
        files = bundle(destination)
        if args.dry_run:
            print("Validated deployment bundle: " + ", ".join(files))
            return
        token = os.getenv("HF_DEPLOY_TOKEN")
        if not token:
            raise SystemExit("Set HF_DEPLOY_TOKEN with write access to the target Space.")
        from huggingface_hub import HfApi

        api = HfApi(token=token)
        previous = api.space_info(args.space).sha
        result = api.upload_folder(
            repo_id=args.space,
            repo_type="space",
            folder_path=directory,
            commit_message="Deploy tested Voice Assistant from GitHub",
            parent_commit=previous,
        )
        print(f"Uploaded {len(files)} files to {args.space}: {result.oid}")
        verify_deployment(api, args.space, result.oid)


if __name__ == "__main__":
    main()
