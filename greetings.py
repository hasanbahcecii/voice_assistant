import json
import os


class Greetings:
    def __init__(self):
        self.greetings_file = "greetings.json"
        self.greetings = self.load_greetings()


    def load_greetings(self):

        if os.path.exists(self.greetings_file):
            try:
                with open(self.greetings_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass  # If the JSON is invalid, ignore the error and use default greetings
                print("Error: Invalid JSON in greetings file.")

        default_greetings = {
            "hello": ["Hello! How can I assist you today?", "Hi there! What can I do for you?"],
            "hi": ["Hi! How can I assist you today?", "Hello there! What can I do for you?"],
            "morning": ["Good morning! How can I assist you today?", "Morning! What can I do for you?"],
            "afternoon": ["Good afternoon! How can I help you?", "Afternoon! What can I do for you?"],
            "evening": ["Good evening! How can I assist you?", "Evening! What can I do for you?"],
            "night": ["Good night! How can I help you?", "Night! What can I do for you?"],
            "goodbye": ["Goodbye! Have a great day!", "See you later! Take care!"],
            "bye": ["Goodbye! Have a great day!", "See you later! Take care!"]
        }

        with open(self.greetings_file, "w", encoding="utf-8") as f:
            json.dump(default_greetings, f, ensure_ascii=False, indent=4)

        return default_greetings

    def answer_greeting(self, text):

        text = text.lower()
        for key in self.greetings:
            if key in text:
                print(f"Greeting matched: {key}")  # Debug statement to show which greeting was matched
                print(f"Available greetings for '{key}': {self.greetings[key]}")  # Debug statement to show available greetings
                return self.greetings[key][0]  # Return the first greeting for the matched key
       
        return None


def main():
    greetings = Greetings()
    print("Welcome to the Greeting Bot! Type a greeting to get a response.")

    while True:
        text = input("Write something: ")
        
        if text.lower() in ["exit", "quit"]:
            print("Goodbye! Have a great day!")
            break

        
        response = greetings.answer_greeting(text)

        if response:
            print(f"Assistant: {response}")
        else:
            print("Sorry, I didn't recognize that greeting. Please try again.")


if __name__ == "__main__":    
    main()