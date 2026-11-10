"""Selectable cloud keyword detection or optional offline Vosk detection."""

import json
from pathlib import Path
import speech_recognition as sr
from settings import GOOGLE_STT_ENDPOINT
from greetings import normalize
from speech import SpeechError


class WakeWordDetector:
    def __init__(self, device_index=None, language="en-US", engine="google", model_path="", timeout=30):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 0.7
        self.recognizer.operation_timeout = timeout
        self.mic = sr.Microphone(device_index=device_index)
        self.language = language
        self.wake_word = "hey asistan" if language == "tr-TR" else "hey assistant"
        self.model = None
        if engine == "vosk":
            if not Path(model_path).is_dir() or not model_path:
                raise ValueError("Set WAKE_MODEL_PATH to a downloaded Vosk model directory.")
            from vosk import Model

            self.model = Model(model_path)

    def MicrophoneSetup(self):
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

    def ListenForWakeWord(self):
        with self.mic as source:
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=4)
                if self.model is None:
                    text = self.recognizer.recognize_google(audio, language=self.language, endpoint=GOOGLE_STT_ENDPOINT)
                else:
                    from vosk import KaldiRecognizer

                    detector = KaldiRecognizer(self.model, 16000)
                    detector.AcceptWaveform(audio.get_raw_data(convert_rate=16000, convert_width=2))
                    text = json.loads(detector.FinalResult()).get("text", "")
                words = normalize(text).split()
                target = self.wake_word.split()
                return any(words[i : i + len(target)] == target for i in range(len(words)))
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                return False
            except sr.RequestError as exc:
                raise SpeechError(
                    "Wake-word recognition is unavailable. Try WAKE_ENGINE=vosk for offline wake detection."
                ) from exc


if __name__ == "__main__":
    detector = WakeWordDetector()
    detector.MicrophoneSetup()
    try:
        while not detector.ListenForWakeWord():
            pass
        print("Wake word detected.")
    except KeyboardInterrupt:
        pass
