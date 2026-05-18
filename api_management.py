import os
import json

class APIManager:
    def __init__(self):
        self.config_file = 'api_keys.json'
        self.load_api_keys()

    def create_config_template(self):
        template = {
            "openai_api_key": "your_openai_api_key_here",
            "huggingface_api_key": "your_huggingface_api_key_here"
        }

        with open(self.config_file, 'w', encoding = "utf-8") as f:
            json.dump(template, f, indent=4)

            print(f"Config template created at {self.config_file}.")
            print("Please fill in your API keys.")
    
    def load_api_keys(self):

        if not os.path.exists(self.config_file):
            print(f"Config file not found: {self.config_file}, creating a config template.")
            self.create_config_template()
            return
        
        try:
            with open(self.config_file, 'r', encoding = "utf-8") as f:
                self.api_keys = json.load(f)
            os.environ['OPENAI_API_KEY'] = self.api_keys.get('openai_api_key', '')
            os.environ['HUGGINGFACE_API_KEY'] = self.api_keys.get('huggingface_api_key', '')
            print("API keys loaded successfully.")  

        except FileNotFoundError:
            print(f"Config file not found: {self.config_file}")
        except json.JSONDecodeError:
            print(f"Invalid JSON in config file: {self.config_file}")   

    def check_api_keys(self):
        openai_key = os.getenv('OPENAI_API_KEY')
        huggingface_key = os.getenv('HUGGINGFACE_API_KEY')

        if openai_key and openai_key != "your_openai_api_key_here":
            print("OpenAI API key is set.")

        else:
            print("OpenAI API key is not set. Please update the config file.")



        if huggingface_key and huggingface_key != "your_huggingface_api_key_here":
            print("Hugging Face API key is set.")   
        else:
            print("Hugging Face API key is not set. Please update the config file.")        



def main():
    api_manager = APIManager()
    api_manager.check_api_keys()                
            
    print("\nHow to get API keys:")
    print("1. OpenAI API Key: Sign up at https://platform.openai.com/signup and create an API key in the dashboard.") 
    print("2. Hugging Face API Key: Sign up at https://huggingface.co/join and create an API key in your account settings.")               

if __name__ == "__main__":
    main()    