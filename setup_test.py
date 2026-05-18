import sys

def setup_test():
    print("setup test is starting...")


    print(f"Python version: {sys.version}")


    librarieries =[
        "speech_recognition",
        "transformers",
        "torch",
        "pytgame",
        "edge_tts",
        "sklearn",
        "numpy"
    ]
    
    for library in librarieries:
        try:
            __import__(library)
            print(f"{library} is installed.")
        except ImportError:
            print(f"{library} is not installed. Please install it before running the tests.")

if __name__ == "__main__":
    setup_test()            