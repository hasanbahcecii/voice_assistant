---
title: Voice Assistant
emoji: 🎙️
colorFrom: purple
colorTo: blue
sdk: gradio
sdk_version: 6.15.1
python_version: '3.13'
app_file: app.py
pinned: false
license: mit
---

# Voice Assistant

A browser and local CLI voice assistant with English/Turkish speech recognition,
streaming OpenAI or Hugging Face chat, and Edge TTS. Web and CLI share one response
service. Recent conversation history belongs to each session and is capped at eight
turns by default.

[Live Space](https://huggingface.co/spaces/hasanbahceci/voice-assistant)

## Modes

- **Demo:** no LLM credentials needed. Complete greetings receive prepared replies;
  other questions explain that this is a demo. It does not pretend to answer with a model.
- **OpenAI:** hosted chat completions using the current Python SDK interface.
- **Hugging Face:** hosted chat inference via `InferenceClient`, not a local extractive
  QA model. Choose an `HF_MODEL` and `HF_PROVIDER` combination available to your account.
- **Auto:** uses OpenAI when its key is set, otherwise Hugging Face when its token is set,
  otherwise Demo. A broken or incomplete real-provider configuration reports an error;
  it does not silently replace the provider with canned answers.

Only **wake detection** can optionally run offline with Vosk. Google STT, hosted LLMs
and Edge TTS require a network connection. Local audio uses SpeechRecognition's adaptive
energy threshold and pause detection; there is no separate neural VAD model.

## Install and run the web app

Python 3.12 or 3.13 is supported. The Space uses Python 3.13 and Gradio 6.15.1.

```bash
git clone https://github.com/hasanbahcecii/voice_assistant.git
cd voice_assistant
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python app.py
```

The web app records audio in the **browser**; the server needs no microphone, PyAudio,
pygame, PyTorch or downloaded model weights. You can type instead of recording and turn
off voice output for a text-only request. Typed text takes precedence if both are supplied.
Select English or Turkish, choose a provider, then Send. Clear conversation resets session
history. Changing language or provider also resets it. Record at most 30 seconds; uploads
are limited to 10 MB. Model output appears as tokens arrive, followed by audio.

## Configuration

Use shell environment variables locally and **Settings → Secrets/Variables** on the Space.
`.env.example` is a reference; the app does not automatically load `.env` files.

| Variable | Default | Purpose |
|---|---|---|
| `BACKEND` | `auto` | `auto`, `demo`, `openai`, `huggingface` |
| `ASSISTANT_LANGUAGE` | `en-US` | `en-US` or `tr-TR` |
| `OPENAI_API_KEY` | empty | OpenAI credential (Secret) |
| `OPENAI_MODEL` | `gpt-3.5-turbo` | Preserved original model; set an accessible chat model |
| `HF_TOKEN` | empty | Token with inference-provider permission (Secret) |
| `HUGGINGFACE_API_KEY` | empty | Legacy alias for `HF_TOKEN` |
| `HF_MODEL` | empty | Required HF chat model ID; no large model is loaded into the Space |
| `HF_PROVIDER` | `auto` | Inference provider supporting that model |
| `API_TIMEOUT` | `30` | Per-request timeout in seconds, 1–120 |
| `MAX_TOKENS` | `256` | Maximum generated tokens, 1–2048 |
| `HISTORY_TURNS` | `8` | Retained recent turns, 1–32 |
| `MICROPHONE_INDEX` | system default | Local CLI input device |
| `WAKE_ENGINE` | `google` | `google` or optional `vosk` |
| `WAKE_MODEL_PATH` | empty | Downloaded Vosk model directory, matching the spoken language |

For example:

```bash
export BACKEND=openai
export OPENAI_API_KEY='your-real-key'
export ASSISTANT_LANGUAGE=tr-TR
python app.py
```

An optional local `api_keys.json` can contain `openai_api_key` and `huggingface_api_key`.
Run `python api_management.py` to create a template without overwriting an existing file.
Environment credentials win. The legacy `api_key.json` filename is supported for migration;
both names are gitignored. Relative config files are resolved against the source directory,
not the launch directory. Never put real keys in `.env.example`, README or committed files.

Provider authentication, quota and model availability must be tested with your account.
The app does not spend tokens testing connectivity during startup.

## Local CLI and microphone

```bash
# Linux microphone support may need: sudo apt install portaudio19-dev python3-dev
python -m pip install -r requirements-local.txt
python scan_input_devices.py
python voice_assistant_openai.py --language tr-TR --microphone 0
python voice_assistant_hgface.py --language en-US
# Keyboard-only mode needs only requirements.txt:
python cli.py --text --backend demo
python openai_apikey_model.py
```

Say **“Hey assistant”** (English) or **“Hey asistan”** (Turkish), pause, then give your
command. Wake detection has a 4-second phrase limit and command capture has a 30-second
limit. Only complete exit commands (`exit`, `quit`, `goodbye`, `çıkış`, `kapat`, `güle güle`)
stop the CLI; questions containing those words remain valid. If voice output fails,
the text response remains available.

For optional offline wake detection:

```bash
python -m pip install -r requirements-offline-wake.txt
# Download a matching-language model from https://alphacephei.com/vosk/models
export WAKE_ENGINE=vosk
export WAKE_MODEL_PATH='/absolute/path/to/downloaded-model'
python voice_assistant_openai.py
```

The app never downloads a Vosk model automatically. Optional local audio/Vosk dependencies
are excluded from the Space build. Actual hardware support depends on the host audio drivers.

## Tests and timing

```bash
python -m pip install -r requirements-dev.txt
python -m pip check
ruff check .
pytest -q
python setup_test.py            # add --local for local audio imports
python scripts/deploy_space.py --dry-run
python scripts/benchmark.py --backend demo --runs 5
```

Tests cover regressions, session isolation, streaming and installed-SDK request contracts,
audio failure handling, and an isolated Space bundle. They do **not** prove live API access,
STT accuracy, TTS availability or microphone playback. Real-account smoke checks:

```bash
python scripts/smoke_live.py --backend openai
python scripts/smoke_live.py --backend huggingface
# Optional real WAV recording, for STT and generated audio validation:
python scripts/smoke_live.py --backend openai --audio /path/to/short-recording.wav
```

For optional Linux resource limits during local checks:

```bash
python scripts/run_guarded.py --cpus 2 --reserve-gib 3 -- python -m pytest -q
```

The guard restricts its own process tree to at most four CPU cores, uses low scheduling
priority, disables GPU visibility, and terminates its own job if available RAM falls
below the configured reserve (minimum 3 GiB). It never stops unrelated processes.

The UI reports input processing, first-token, model-completion and total wall times.
No fixed end-to-end latency claim is made: network, provider, text length and speech length
all affect it. Streaming improves when text first becomes visible; TTS starts after the
complete answer. `benchmark.py` records the selected backend and separates first-token
from total response time. Demo timings do not measure cloud performance.

## Deploy to Hugging Face

GitHub and the Space are separate repositories. A GitHub push alone does not update the
Space unless a sync workflow is configured.

1. Add GitHub **environment** `huggingface` (optionally with required reviewers).
2. Add GitHub Actions secret **`HF_DEPLOY_TOKEN`** with write access to the target Space.
   This is a deployment credential; it is separate from inference credentials.
3. Optionally set GitHub variable `HF_SPACE_ID`; default: `hasanbahceci/voice-assistant`.
4. Configure model credentials on the **Space itself**. No credential → Demo. For OpenAI,
   set `OPENAI_API_KEY`; for HF inference set `HF_TOKEN` plus variable `HF_MODEL`.
5. Push approved code changes to GitHub. This runs CI but does **not** deploy the Space.
   After approving a live release, manually run **Deploy Hugging Face Space**.
6. The workflow installs dependencies, runs tests/lint, uploads the allowlisted web bundle,
   waits for the uploaded revision to reach `RUNNING`, then checks its demo API.
   A build failure or failed smoke check fails the deployment job; there is no automatic rollback.

`deploy/space-files.json` explicitly lists published files. The uploader does not copy
local keys, CLI hardware code, tests or Git metadata, and does not delete unrelated remote
files. README contains the required Spaces YAML configuration. Original MP3 files are
removed after Gradio processes them; its served cache expires after ten minutes (checked
every five minutes).

Manual deployment, after reviewing the bundle:

```bash
python scripts/deploy_space.py --dry-run
export HF_DEPLOY_TOKEN='your-space-write-token'
python scripts/deploy_space.py --space hasanbahceci/voice-assistant
```

Keep the prior Space commit available for rollback. A green build verifies the web app's
demo contract; check the configured real provider separately before announcing it as working.

## Data flow

Audio → Google STT (HTTPS) → shared response service → chosen provider → Edge TTS → audio.
Browser text input skips STT. With cloud wake detection, wake clips also go to Google.
With Vosk wake detection, wake clips stay local. Model requests include recent session
history. There is no application database or persistent transcript log (the local CLI prints responses). Third-party
services have their own data handling policies. The public app has a bounded queue and serializes generation requests to avoid concurrent history updates;
provider quotas and billing remain controlled by the owner's account.

## License

MIT. See [LICENSE](LICENSE).
