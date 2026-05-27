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


    def load_api_key(self):
        try:
            with open("api_key.json", "r") as f:
                data = json.load(f)
                api_key = data.get("openai_api_key")
                if not api_key or api_key.startswith("your-openai-api-key-here"):
                    raise ValueError("API key not found in the file.")
                openai.api_key = api_key

        except FileNotFoundError:
            raise FileNotFoundError("API key file not found. Please create 'api_key.json' with your OpenAI API key.")        


    def test_api_connection(self):
        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[{"role": "system", "content": "You are a helpful assistant."},
                          {"role": "user", "content": "Hello, how are you?"}],
                max_tokens=5           
            )
            return True

        except Exception as e:
            raise ConnectionError(f"Failed to connect to OpenAI API: {e}")
        
    def generate_response(self, question):
        if not self.api_key_loaded:
            return "API key not loaded. Please check your configuration.", 0
        
        greetings_answer = self.greetings.answer_greeting(question)

        if greetings_answer:
            return greetings_answer, 1.0
        
        try:
            start_time = time.time()
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[{"role": "system", "content": "You are a helpful assistant."},
                          {"role": "user", "content": question}],
                max_tokens=150,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content.strip()
            token_used = response.usage.total_tokens
            response_time = time.time() - start_time

            print(f"OpenAI response: {answer}")
            print(f"Tokens used: {token_used}")
            print(f"Response time: {response_time:.2f} seconds")

            confidence = 0.85
            return answer, confidence

        except openai.RateLimitError:
            return "Rate limit exceeded. Please try again later.", 0
        except openai.authentication.AuthenticationError:
            return "Authentication failed. Please check your API key.", 0
        except Exception as e:
            return f"An error occurred: {e}", 0
        


def main():
    ai = AIModel()
    
    if not ai.api_key_loaded:
        print("API key not loaded.")
        print("Please check your 'api_key.json' file and ensure it contains your OpenAI API key in the following format:")
        print('{\n    "openai_api_key": "your-openai-api-key-here"\n}')
        print("After updating the file, restart the application.")
        return
    
    print("AI model testing...")
    print("Type 'exit' to quit.")

    while True:
        question = input("Ask something or type 'exit' to quit: ")
        if question.lower() == "exit":
            print("Exiting...")
            break   

        answer, confidence = ai.generate_response(question)

        if confidence == 1.0:
            print(f"Answered with greetings module.")
        else:
            print(f"Answered with OpenAI.")


        print(f"Answer: {answer}")
        print(f"Confidence: {confidence:.2f}")


if __name__ == "__main__":    main()