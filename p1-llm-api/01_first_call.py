import anthropic
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # finds ai-eng-jny/.env and loads ANTHROPIC_API_KEY

USE_LOCAL = True  # True = free Gemma on Ollama, False = real Claude (needs credits)

if USE_LOCAL:
    client = Anthropic(base_url="http://localhost:11434", api_key="ollama")
    MODEL = "gemma3:1b"
else:
    client = Anthropic()  # uses ANTHROPIC_API_KEY loaded from .env
    MODEL = "claude-haiku-5-5"

try:
    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[
            {"role": "user", "content": input("Ask: ")}
        ],
    )
    print(response.content[0].text)
    print("stop_reason:", response.stop_reason)
    print("tokens in/out:", response.usage.input_tokens, response.usage.output_tokens)

except anthropic.APIConnectionError:
    print("Can't reach the model server. Is Ollama running?")
except anthropic.NotFoundError:
    print(f"Model '{MODEL}' not found. Check the name / run `ollama list`.")
except anthropic.APIStatusError as e:
    print(f"API error {e.status_code}: {e.message}")
