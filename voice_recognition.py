import speech_recognition as sr 
import time 

class VoiceToText:
    # Pass the working device_index via the constructor
    def __init__(self, device_index=None):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300 
        self.recognizer.pause_threshold = 0.5  
        
        # OPTIMIZATION: Instantiate the microphone OS-binding ONLY ONCE.
        # This prevents PyAudio from probing ALSA devices on every single listen loop.
        self.mic = sr.Microphone(device_index=device_index)

    def AdjustMicrophone(self):
        print("Initializing microphone and adjusting for ambient noise...")
        # Reuse the pre-initialized mic object
        with self.mic as source:
            print("Adjusting for ambient noise, please wait...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Adjustment complete.")

    def SingleListen(self):
        print("Speaking... Please say something.")

        # Reuse the pre-initialized mic object
        with self.mic as source:
            try:
                # Listen with timeouts to prevent the thread from hanging indefinitely
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)  
                print("Processing your speech...")
                
                # Cloud API call (Consider replacing with local Vosk/Whisper for Edge AI)
                command = self.recognizer.recognize_google(audio, language="en-US")
                print(f"You said: {command}")
                return command
                
            except sr.WaitTimeoutError:
                print("Listening timed out while waiting for phrase to start.")
                return None
            except sr.UnknownValueError:
                print("Sorry, I could not understand the audio. (Check if correct mic is targeted)")
                return None
            except sr.RequestError as e:
                print(f"Network/API Error: Could not request results from Google; {e}")
                return None
            
def main():
    # INJECT YOUR HARDWARE INDEX HERE (e.g., 3). 
    # Find this using the sr.Microphone.list_microphone_names() script we ran earlier.
    TARGET_MIC_INDEX = 7 
    
    voice_to_text = VoiceToText(device_index=TARGET_MIC_INDEX)
    voice_to_text.AdjustMicrophone()
    
    while True:
        print("\n 1. Single Listen  2. Exit")
        choice = input("Enter your choice: ")
        
        if choice == "1":
            command = voice_to_text.SingleListen()
            if command:
                print(f"Recognized Command: {command}")
            else:
                print("No command recognized. Please try again.")
        elif choice == "2":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")
            
        time.sleep(1)       

if __name__ == "__main__":
    main()