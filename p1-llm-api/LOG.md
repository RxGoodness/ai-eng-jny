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

---

## 2026-10-31 — Anthropic API Fundamentals, Lesson 2: Messages format

### What I built
- `llm_config.py`: a shared client + `MODEL` setup with a `USE_LOCAL` switch, so every script imports it instead of copying the setup.
- `02_translate.py`: a `translate(word, language)` function that returns only the translated word (`Hola`, `pollo`). It uses a strict prompt and `.strip()` to remove stray whitespace and newlines.
- `02_chatbot.py`: a multi-turn terminal chatbot. It keeps a `history` list, quits on `quit`, handles API errors, and prints the input token count and history length after each turn.

### Key insights
- **Memory = the history list.** The model remembers nothing between calls. Each request sends the whole conversation, so the `history` list *is* the bot's memory. Without appending the assistant reply, it forgot my name.
- **The cost of a conversation grows every turn.** The whole history is re-sent each time, so `input_tokens` keeps rising. Long chats get slower and more expensive.
- A message is `{"role": "user" | "assistant", "content": ...}`, and `response.content` is a **list** of blocks, which is why I write `content[0].text`.
- Message list rules: start with `user`, and alternate `user` and `assistant`. If an API call fails, remove the unanswered user message (`history.pop()`) so the history doesn't end up with two `user` messages in a row.

### Gemma (Ollama) vs Claude: differences I saw
| Topic | What the notebook says (Claude) | What happened with `gemma3:1b` |
|-------|---------------------------------|--------------------------------|
| Wrong message order (starting with `assistant`, two `assistant` in a row) | Error | **No error.** Gemma just answered. |
| Prefill ("putting words in Claude's mouth") | Claude continues from my partial assistant message | **Worked on Gemma**: it continued "calming mountain air…". But **current Claude models (Haiku 5.5, Sonnet 5.5, Opus 5.5) reject prefill with a 400 error.** The notebook was written for older models. On today's Claude, use instructions in the prompt or a system prompt instead. |
| Few-shot (pickle sentiment) | Replies `POSITIVE` | **Ignored the examples** and chatted ("Wow, that's fantastic!…"). A 1B model is too small to pick up the pattern reliably. Fix: an explicit instruction ("Reply with only POSITIVE or NEGATIVE") or a bigger model (`gemma3:4b`). |

### Lessons
- **Not getting an error doesn't mean my input was right. Different servers check different things.** Ollama accepted messages that Claude's API would reject, so my code should follow the rules itself instead of relying on the server to catch mistakes.
- A technique from a tutorial can stop working on newer models (prefill). Check the current docs before relying on it.
- Model size affects how well a model follows examples and instructions (preview of Lesson 3).

### One thing I'm curious about
- What do real chat apps do when the history gets too long for the model's context window, or too expensive to keep re-sending?
