"""Bounded microphone capture with adaptive energy and pause-based VAD."""

import speech_recognition as sr
from settings import GOOGLE_STT_ENDPOINT
from speech import SpeechError


class VoiceToText:
    def __init__(self, device_index=None, language="en-US", timeout=30):
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.7
        self.recognizer.operation_timeout = timeout
        self.language = language
        self.mic = sr.Microphone(device_index=device_index)

    def AdjustMicrophone(self):
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

    def SingleListen(self):
        with self.mic as source:
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=30)
                return self.recognizer.recognize_google(audio, language=self.language, endpoint=GOOGLE_STT_ENDPOINT)
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                return None
            except sr.RequestError as exc:
                raise SpeechError("Speech recognition is unavailable. Check your connection.") from exc

    ListenForCommand = SingleListen


if __name__ == "__main__":
    from settings import Settings

    config = Settings.from_env()
    listener = VoiceToText(config.microphone_index, config.language, config.timeout)
    listener.AdjustMicrophone()
    print(listener.SingleListen())
