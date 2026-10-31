import time

from llm_config import client

MODELS = ["gemma3:1b"]  # add more pulled models here to compare them


def run(model, prompt, max_tokens=500):
    start = time.perf_counter()
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    seconds = time.perf_counter() - start
    return response.content[0].text.strip(), seconds, response.usage.output_tokens


SPEED_TASK = "Explain the concept of photosynthesis in a concise paragraph."

print(f"{'model':<12} {'tokens':>6} {'seconds':>8} {'tok/s':>6}")
for model in MODELS:
    run(model, "hi", max_tokens=5)  # warm-up: load the model so loading time isn't measured
    text, seconds, tokens = run(model, SPEED_TASK)
    print(f"{model:<12} {tokens:>6} {seconds:>8.2f} {tokens / seconds:>6.1f}")
