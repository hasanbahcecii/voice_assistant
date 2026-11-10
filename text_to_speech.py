"""Local playback only. Web deployments use speech.py and need no pygame."""

from pathlib import Path
from speech import synthesize_sync


class TextToSpeech:
    def __init__(self, language="en-US", timeout=30):
        self.language = language
        self.timeout = timeout

    def speak(self, text):
        path = synthesize_sync(text, self.language, self.timeout)
        try:
            self.play_speech(path)
        finally:
            Path(path).unlink(missing_ok=True)

    def play_speech(self, file_path):
        import pygame

        pygame.mixer.init()
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            clock = pygame.time.Clock()
            while pygame.mixer.music.get_busy():
                clock.tick(20)
        finally:
            pygame.mixer.music.unload()
            pygame.mixer.quit()


if __name__ == "__main__":
    TextToSpeech().speak("Hello! This is a voice output test.")
