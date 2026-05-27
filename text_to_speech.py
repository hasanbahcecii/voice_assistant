from email.mime import text

import edge_tts
import pygame
import asyncio
import tempfile
import os


class TextToSpeech:
    def __init__(self):
        self.voice = "en-US-JennyNeural"
        pygame.mixer.init()


    async def text_to_speech_file(self, text):
        print(f"Generating speech for: {text[:30]}...")  # Print the first 30 characters for brevity
        
        # Create a temporary file to store the generated speech

        comm = edge_tts.Communicate(
            text = text, 
            voice = self.voice,
            rate = "+5%",
            volume = "+75%",
            pitch="-20Hz"
            )
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")

        await comm.save(temp_file.name)  # Save the generated speech to the temporary file
        return temp_file.name  # Return the path to the temporary file
        print(f"Finished generating speech for: {text[:30]}...")  # Print the first 30 characters for brevity

    def play_speech(self, file_path):
        
        print(f"Playing speech for: {file_path[:30]}...")  # Print the first 30 characters for brevity
        
        try:
            pygame.mixer.music.unload()  # Unload any previously loaded speech file
        except pygame.error:
            pass  # No music was loaded, ignore the error

        
        pygame.mixer.music.load(file_path)  # Load the generated speech file
        pygame.mixer.music.set_volume(0.95)  # Set volume to maximum       
        pygame.mixer.music.play()  # Play the speech file

        clock = pygame.time.Clock()

        while pygame.mixer.music.get_busy():
            clock.tick(10)  # Check every 100ms if the music is still playing

        pygame.mixer.music.unload()  # Unload the speech file after playing
        os.remove(file_path)  # Remove the temporary file after playing
        print(f"Finished playing: {file_path}...")  # Print the first 30 characters for brevity
        

    def speak(self, text):

        file = asyncio.run(self.text_to_speech_file(text))
        self.play_speech(file)



def main():
    tts = TextToSpeech()
    tts.speak("Hello, this is a test of the text to speech system. I hope you find it useful!")
    
    while True:
        print("1. Enter text to speak")
        print("2. Exit")
        choice = input("Choose an option: ")
        if choice == "1":
            text = input("Enter text to speak: ")
            tts.speak(text) 
        elif choice == "2":
            print("Exiting...")
            break


if __name__ == "__main__":
    main()






