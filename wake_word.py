from pdb import main

import speech_recognition as sr
import time

class WakeWordDetector:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.pause_threshold = 0.5
        self.wake_word = "Hey assistant"

    def MicrophoneSetup(self): 
        print("Setting up microphone...") 
        with sr.Microphone() as source:
            print("Adjusting for ambient noise, please wait...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Microphone setup complete.")  
        self.mic = sr.Microphone()

    def ListenForWakeWord(self):
        print(f"Listening for wake word: '{self.wake_word}'...")
        with self.mic as source:
            while True:
                try:
                    audio = self.recognizer.listen(source, timeout=5)
                    print("Processing audio...")
                    text = self.recognizer.recognize_google(audio)
                    print(f"Heard: {text}")
                    if self.wake_word.lower() in text.lower():
                        print("Hey Assistant detected!")
                        return True
                except sr.WaitTimeoutError:
                    print("Listening timed out, retrying...")
                except sr.UnknownValueError:
                    print("Could not understand audio, retrying...")
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")
                time.sleep(0.1)


def main():
    detector = WakeWordDetector()
    detector.MicrophoneSetup()
    print("Ctrl + C to exit.")

    try:
        while True:
            if detector.ListenForWakeWord():
                print("Wake word detected! You can now give a command.")
                time.sleep(2)  # Simulate processing time for command

    except KeyboardInterrupt:
        print("\nExiting wake word detector. Goodbye!")            


if __name__ == "__main__":
    main()