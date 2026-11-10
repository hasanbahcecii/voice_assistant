"""STT without server audio hardware, plus safe temporary TTS files."""

import asyncio
from pathlib import Path
import tempfile
import wave
from settings import LANGUAGES, GOOGLE_STT_ENDPOINT


class SpeechError(RuntimeError):
    pass


def recognize_file(path, language="en-US", max_seconds=30, timeout=30):
    import speech_recognition as sr

    recognizer = sr.Recognizer()
    recognizer.operation_timeout = timeout
    try:
        with sr.AudioFile(str(path)) as source:
            if source.DURATION > max_seconds:
                raise SpeechError(f"Record at most {max_seconds} seconds.")
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio, language=language, endpoint=GOOGLE_STT_ENDPOINT)
    except sr.UnknownValueError as exc:
        raise SpeechError("Speech could not be understood. Please record again.") from exc
    except sr.RequestError as exc:
        raise SpeechError("Speech recognition is unavailable. Try text input.") from exc
    except (OSError, ValueError, EOFError, wave.Error) as exc:
        raise SpeechError("The audio file could not be read. Record a new clip.") from exc


async def synthesize(text, language="en-US", timeout=30):
    import edge_tts

    # Close before Edge opens it; important on Windows.
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as handle:
        path = Path(handle.name)
    try:
        communicate = edge_tts.Communicate(text, LANGUAGES[language])
        await asyncio.wait_for(communicate.save(str(path)), timeout=timeout)
        if not path.stat().st_size:
            raise SpeechError("Speech generation returned no audio.")
        return str(path)
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def synthesize_sync(text, language="en-US", timeout=30):
    try:
        return asyncio.run(synthesize(text, language, timeout))
    except Exception as exc:
        raise SpeechError("Voice output is unavailable; the text response is still available.") from exc
