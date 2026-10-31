from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

USE_LOCAL = True  # True = free Gemma on Ollama, False = real Claude (needs credits)

if USE_LOCAL:
    client = Anthropic(base_url="http://localhost:11434", api_key="ollama")
    MODEL = "gemma3:1b"
else:
    client = Anthropic()
    MODEL = "claude-haiku-5-5"
