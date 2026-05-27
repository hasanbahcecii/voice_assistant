from transformers import pipeline
import time
import json
from greetings import Greetings


class AIModel:
    def __init__(self):
        self.api_key_loaded = False
        self.model_name = "deepset/minilm-uncased-squad2"
        self.qa_pipeline = None
        self.greetings = Greetings()
        self.load_model()

    def load_model(self):
        print("Loading Transformers model...")
        start_time = time.time()
        try:
            with open("api_keys.json", "r") as file:
                keys = json.load(file)
            hf_token = keys.get("huggingface_api_key")

            self.qa_pipeline = pipeline(
                model=self.model_name,
                token=hf_token,
            )

            print(f"Model loaded successfully in {time.time() - start_time:.2f} seconds.")
            self.api_key_loaded = True
        except Exception as e:
            print(f"Failed to load model: {e}")
            self.api_key_loaded = False

    def test_model_connection(self):
        try:
            self.load_model()
            test_context = "The capital of Turkiye is Ankara."
            test_question = "What is the capital of Turkiye?"
            result = self.qa_pipeline(question=test_question, context=test_context)
            if not result or "answer" not in result:
                raise ValueError("Model did not return a valid answer.")
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to model: {e}")

    def generate_response(self, question):
        if not self.api_key_loaded:
            return "Model is not loaded. Please check the API key and try again.", 0.0

        greeting = self.greetings.answer_greeting(question)
        if greeting:
            return greeting, 1.0

        context = (
            "The capital of Turkiye is Ankara. "
            "The capital of France is Paris. "
            "The capital of the United States is Washington, D.C. "
            "The capital of Germany is Berlin. "
            "The capital of Japan is Tokyo. "
            "The capital of the United Kingdom is London. "
            "Python is a high-level programming language created by Guido van Rossum in 1991. "
            "JavaScript is a programming language commonly used for web development. "
            "The Earth orbits the Sun and has one natural satellite called the Moon. "
            "Water boils at 100 degrees Celsius at sea level. "
            "The speed of light is approximately 300,000 kilometers per second. "
            "Albert Einstein developed the theory of relativity. "
            "The largest ocean on Earth is the Pacific Ocean. "
            "The tallest mountain in the world is Mount Everest at 8,849 meters."
        )

        try:
            start_time = time.time()
            result = self.qa_pipeline(question=question, context=context)
            answer = result.get("answer", "Sorry, I could not find an answer.")
            confidence = result.get("score", 0.0)
            process_time = time.time() - start_time
            print(f"Response generated in {process_time:.2f}s, confidence {confidence:.2f}")
            return answer, confidence
        except Exception as e:
            return f"Error generating response: {e}", 0.0


def main():
    model = AIModel()
    if not model.api_key_loaded:
        print("Model failed to load.")
        print("Please check your API key and try again.")
        return

    print("Model test started...")
    print("Type 'exit' to quit.")
    while True:
        question = input("Ask some question (or type 'exit' to quit): ")
        if question.lower() == "exit":
            print("Exiting the program. Goodbye!")
            break
        response, confidence = model.generate_response(question)
        print(f"Answer: {response} (Confidence: {confidence:.2f})\n")


if __name__ == "__main__":
    main()