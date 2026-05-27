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
            self.tts = TextToSpeech()
            print("VoiceAIModel initialized successfully.")
        
        if self.api_key_loaded:
            print("Setting up microphone.")

            self.speech_recognizer.AdjustMicrophone()
            self.wake_word_detector.MicrophoneSetup()
            print("VoiceAIModel is ready to listen for wake word. ")
            print("Say 'Hey Assistant' to activate the voice assistant.")

        else:
            print("Voice Assistant is not initialized due to missing API key.")  


def main():
    try:
        print("-" * 50)
        print ("Voice Assistant")
        print("-" * 50)

        ai = VoiceAIModel()

        if not ai.api_key_loaded:
            print("Exiting due to missing API key.")
            return
        
        print("Voice Assistant is running. Say 'Hey Assistant' to activate.")
        print("Say 'exit' to quit the assistant.")

        print("-" * 50)

        session_start = time.time()
        question_count = 0

        while True:
            try:
                if ai.wake_word_detector.ListenForWakeWord():
                    continue
                print("Hey assistant detected! Listening for command...")
                ai.tts.speak("Yes, how can I assist you?")

                command = ai.speech_recognizer.ListenForCommand()
                
                if not command:
                    ai.tts.speak("Sorry, I didn't catch that. Please try again.")
                    continue

                print(f"Command {question_count + 1} received: {command} ")

                if any(exit_word in command.lower() for exit_word in ["exit", "quit", "goodbye"]):
                    ai.tts.speak("Goodbye! Have a great day!")
                    break  
                

                with Timer("Total Q-A time"):
                    response, confidence = ai.generate_response(command)
                    ai.tts.speak(response)
                    question_count += 1

                if confidence == 1.0:
                    print("Answered with greetings module.")

                else:
                    print("Answered with main OpenAI model.")

                

                print(f"Answer: {response} | Confidence: {confidence}")

                print("For a new command, say 'Hey Assistant' again.")
                print("-" * 50)

            except KeyboardInterrupt:
                print("\nExiting Voice Assistant. Goodbye!")
                break   
            except Exception as e:
                print(f"An error occurred: {e}")
                ai.tts.speak("Sorry, an error occurred. Please try again.")
                

        total_session_time = time.time() - session_start        
        print(f"Total session time: {total_session_time:.2f} seconds")
        print(f"Total questions answered: {question_count}")
        print("Thank you for using the Voice Assistant!")
        print("-" * 50)
        
    except Exception as e:
        print(f"An error occurred during initialization: {e}")





if __name__ == "__main__":    main()
