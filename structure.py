import time

class Timer:
    def __init__(self, name):
        self.start_time = None
        self.name = name


    def __enter__(self):
        self.start_time = time.time()
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.time()
        minutes = int((end_time - self.start_time) / 60)
        seconds = int(end_time - self.start_time) % 60
        print(f"{self.name} took {minutes} minutes and {seconds} seconds.")

class BasicAssistant:
    def __init__(self, name):
        self.name = name

    def assist(self):
        print(f"{self.name} is assisting you with your tasks.")
        self.wake_word = "Hey Assistant"
        print(f"To activate {self.name}, say '{self.wake_word}'.")

    def test_timer(self):
        with Timer("Test"):
            time.sleep(2)  # Simulate a task that takes 2 seconds    
            print("Test completed.")


def main():
    assistant = BasicAssistant("MyAssistant")
    assistant.assist()
    assistant.test_timer()       
    print(f"Wake Word: {assistant.wake_word}")     

if __name__ == "__main__":
    main()