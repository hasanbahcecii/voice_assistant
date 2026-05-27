from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline
import time
import json
from greetings import Greetings


class AIModel:

    def __init__(self):
        self.apikeyloaded = False
        self.model_name = "deepset/roberta-base-squad2"
        self.tokenizer = None
        self.model = None
        self.qa_pipeline = None
        self.greetings = Greetings()
        self.load_model()


    def load_model(self):
        print("Loading Transformers model...")
        start_time = time.time()
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForQuestionAnswering.from_pretrained(self.model_name)
            self.qa_pipeline = pipeline("question-answering",
                                        model=self.model,
                                        tokenizer=self.tokenizer,
                                        max_answer_length=100,
                                        min_answer_length=10)
            print(f"Model loaded successfully in {time.time()-start_time:.2f} seconds.")
            self.apikeyloaded = True
        except Exception as e:
            print(f"Failed to load model: {e}")
            self.apikeyloaded = False
        

    def test_model_connection(self):
        try:
            self.load_model()
            test_context = "The capital of Turkiye is Ankara."
            test_question = "What is the capital of Turkiye?"
            result = self.qa_pipeline(question=test_question, context=test_context)
            if not result or 'answer' not in result:
                raise ValueError("Model did not return a valid answer.")
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to model: {e}")    
        
    def generate_response(self, question):
        if not self.apikeyloaded:
            return "Model is not loaded. Please check the API key and try again."

        context = "The capital of Turkiye is Ankara."  # This is a simple context for testing. In a real application, you would use a more relevant and comprehensive context.
        try:
            start_time = time.time()
            result = self.qa_pipeline(question=question, context=context)
            answer = result.get('answer', 'Sorry, I could not find an answer.')
            confidence = result.get('score')
            process_time = time.time() - start_time
            print(f"Response generated in {process_time:.2f} seconds with confidence {confidence:.2f}.")
            return answer, confidence
        except Exception as e:
            return f"Error generating response: {e}"    
        


def main():
    model = AIModel()
    if not model.apikeyloaded:
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

              


if __name__ == "__main__":    main()
