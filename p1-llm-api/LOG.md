# Learning Log

## 2026-10-31 — Anthropic API Fundamentals, Lesson 1: Getting started

### What I built
- Ran `01_getting_started.ipynb` and got my first LLM response (a chicken haiku).
- Wrote `01_first_call.py`:
  - loads `.env` with `load_dotenv()`
  - has a `USE_LOCAL` switch: free Gemma (`gemma3:1b`) on Ollama, or real Claude (`claude-haiku-5-5`)
  - sends a message with `client.messages.create()` and prints `response.content[0].text`
  - prints `stop_reason` and token usage
  - handles connection, not-found and other API errors with `try/except`
  - takes the question from `input("Ask: ")`

### Errors I hit and what they meant
| # | Error | What it meant | Fix |
|---|-------|---------------|-----|
| 1 | `TypeError: Could not resolve authentication method` | **Key layer:** the client had no API key. `load_dotenv()` looks in the notebook's folder and the folders above it, and my `.env` is in a sibling folder, so it found nothing and failed silently (`my_api_key = None`). | `load_dotenv("../../ai-eng-jny/.env")` and check with `print(my_api_key is not None)` |
| 2 | `400 invalid_request_error: credit balance is too low` | **Account layer:** the key and model were fine, but the API account has no credits. API billing is separate from a Claude.ai subscription. Changing the model doesn't help. | Buy API credits (about $5), or use a free local model for now |
| 3 | `404 not_found_error: model 'llama3.2' not found` | **Resource layer:** I reached the server (Ollama), but the model I asked for wasn't downloaded there. | `ollama pull <model>`, then check with `ollama list` |
| 4 | `Error: EOF` on `ollama pull llama3.2` | **Remote layer:** the download stopped at "pulling manifest". Other models downloaded fine, so the problem was that model on the registry, not my network or setup. | Use a different model (`gemma3:1b`) |

### Lessons
- Read the error **type and status code** first. They tell you which layer failed: my code, my key, my account, or the remote resource.
- When debugging, change one thing at a time (here, the model name) to narrow down the cause.
- Code that runs after a `try/except` must not depend on variables that only exist if the `try` succeeded.
- `load_dotenv()` fails silently, so check the key loaded before using it.

### One thing I'm curious about
- Why did the input token count drop from 16 to 5 when I sent the same prompt again? (Prompt caching? How do Claude's API and Ollama each handle it?)
