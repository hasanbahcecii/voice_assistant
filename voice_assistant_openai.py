import time
from openai_apikey_model import AIModel
from wake_word import WakeWordDetector
from voice_recognition import VoiceToText
from text_to_speech import TextToSpeech
from greetings import Greetings
from structure import Timer

class VoiceAIModel(AIModel):    
    def __init__(self):
        # Main AI model initialization (openai_apikey_model)
        super().__init__()

        print("Initializing VoiceAIModel...")

        with Timer("Voice modules initialization"):
            self.wake_word_detector = WakeWordDetector()
            self.speech_recognizer = VoiceToText()
            self.text_to_speech = TextToSpeech()
            print("VoiceAIModel initialized successfully.")


