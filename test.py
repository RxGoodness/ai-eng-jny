from dotenv import load_dotenv
import os

# load_dotenv()
# my_api_key = os.getenv("ANTHROPIC_API_KEY")

load_dotenv("../../ai-eng-jny/.env")
my_api_key = os.getenv("ANTHROPIC_API_KEY")
print("Key loaded:", my_api_key is not None)