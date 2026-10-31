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




## 2026-10-31 — Anthropic API Fundamentals, Lesson 3: Models

### What I built
- `03_compare.py`: a speed benchmark. A `run()` helper times one call with `time.perf_counter()` and returns text, seconds and output tokens, then a table prints tokens, seconds and tokens/second per model.
- `03_compare_practice.py`: an accuracy eval. It asks the fecal coliform maths question 5 times per model and scores exact matches against the correct answer (`18`).
- Ran `03_models.ipynb` against Ollama instead of the retired Claude 3 models.

### Results so far (only `gemma3:1b`; `gemma3:4b` not pulled yet)
Speed, photosynthesis task, model already loaded:

| model | tokens | seconds | tok/s |
|-------|--------|---------|-------|
| gemma3:1b | 85 | 1.68 | 50.7 |
| gemma3:1b | 72 | 1.46 | 49.3 |

Cold start, the same short request twice (from `03_compare.py`):

| run | seconds |
|-----|---------|
| 1st (model loading into memory) | 1.75 |
| 2nd (model already loaded) | 0.08 |

About **22× slower** on the first call.

Accuracy, maths task (correct answer `18`, because the geometric mean is 17.50):

| model | score | answers |
|-------|-------|---------|
| gemma3:1b | 0/5 | `['23', '23', '23', '23', '23']` |

### Key insights
- **Choosing a model is a trade-off between capability, speed and cost, and the only way to choose is to measure it on my own task.** Benchmarks and marketing don't tell me how a model does on *my* prompt.
- **Consistent ≠ correct.** `gemma3:1b` answered `23` every time, so it was confident, repeatable and wrong. Only an eval with a known correct answer catches this.
- **Cold start.** The first request after a model loads is much slower (1.75 s vs 0.08 s). Warm up before timing, or I'm measuring loading instead of the model.
- **Price gap.** Current Claude lineup ($ per 1M tokens, input / output): Haiku 5.5 $0.10 / $0.50, Sonnet 5.5 $2 / $10, Opus 5.5 $4 / $20. Opus costs 40× as much per token as Haiku. The notebook's Claude 3 models are all retired.
- An **eval** is a fixed task + a known correct answer + a score. `03_compare_practice.py` is my first one.

### Errors I hit and what they meant
No crashes this time, but there were **silent bugs**: the code ran and printed plausible numbers, but measured the wrong thing.

| # | Problem | What it meant | Fix |
|---|---------|---------------|-----|
| 1 | `MODELS = ["gemma3:1b", "gemma3:1b"]` | **Code layer:** the same model listed twice, so nothing was actually compared. The second row only looked faster because the model was already loaded. | `ollama pull gemma3:4b` and use `["gemma3:1b", "gemma3:4b"]` |
| 2 | The speed table timed `MATH_TASK` with `max_tokens=50` | **Code layer:** the answer is about 4 tokens, so tokens/second mostly measured request overhead, not generation speed. | Time `SPEED_TASK` (a long answer) with `max_tokens=500` |
| 3 | Warm-up call commented out and placed *after* the timed call | **Code layer:** a warm-up only helps if it runs *before* the timer. | Move `run(model, "hi", max_tokens=5)` above the timed `run(...)` |

### Differences I noticed (tutorial vs what actually happened)
| Topic | What the tutorial says | What actually happened |
|-------|------------------------|------------------------|
| Models | Claude 3 / 3.5 IDs | All retired. I compared Gemma sizes locally instead (1b ≈ Haiku, 4b ≈ Sonnet, 12b ≈ Opus). |
| Maths question | Haiku 3 got 2/7, Sonnet 3.5 got 7/7 | `gemma3:1b` got 0/5, always `23` |
| Speed demo | One call per model | Without a warm-up, the first model looks unfairly slow (cold start) |

### Lessons
- Start with the smallest, cheapest model, test it on the real task with an eval, and move up only if it fails.
- **Sanity-check benchmark output.** Numbers that look plausible can still be wrong. Ask "what exactly did this measure?" (the same model twice, the wrong task, warm-up in the wrong place).
- Warm up before timing anything.

### Model decision
- **Staying with `gemma3:1b`.** `gemma3:4b` (3.3 GB) is more than I want to install, so I didn't run a side-by-side comparison. I understand the method: the same tasks, a warm-up, then compare tok/s and eval scores.
- Trade-off I'm accepting: it's fast (about 50 tok/s) and free, but weak at maths (0/5) and few-shot. For tasks that need accuracy I'll switch `USE_LOCAL = False` and use Claude once I have API credits.
- Fixed the three silent bugs above. `MODELS` now lists only `gemma3:1b`, and `03_compare.py` times `SPEED_TASK` after a warm-up.

### One thing I'm curious about
- How do teams run evals at scale? Hundreds of test cases, scored automatically, rerun every time a prompt or model changes?
