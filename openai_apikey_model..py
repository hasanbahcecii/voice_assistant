import openai
import json
import time
from greetings import Greetings


class AIModel:
    def __init__(self):
        self.api_key_loaded = False 
        self.model_name = "gpt-3.5-turbo"
        self.greetings = Greetings()
        self.load_model()

    def load_model(self):

        print("Loading API key and testing connection...")
        start_time = time.time()

        try:
            self.load_api_key()
            self.test_api_connection()
            print("API key loaded successfully.")

            loading_time = time.time()-start_time
            print(f"Model loaded in {loading_time:.2f} seconds.")

            self.api_key_loaded = True

        except Exception as e:
            print(f"Error loading API key: {e}")
            self.api_key_loaded = False


