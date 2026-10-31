import time

from llm_config import client

MODELS = ["gemma3:1b"]  # add more pulled models here to compare them

RUNS = 5
CORRECT = "18"

def run(model, prompt, max_tokens=500):
    start = time.perf_counter()

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )

    seconds = time.perf_counter() - start

    return (
        response.content[0].text.strip(),
        seconds,
        response.usage.output_tokens,
    )


MATH_TASK = (
    "What is the geometric monthly fecal coliform mean of a distribution "
    "system with the following FC counts: 24, 15, 7, 16, 31 and 23? "
    "The result will be inputted into an NPDES DMR, therefore, round to "
    "the nearest whole number. Respond only with a number and nothing else."
)

print(f"{'model':<15} {'score':>8} {'answers'}")

for model in MODELS:
    answers = [
        run(model, MATH_TASK, max_tokens=50)[0]
        for _ in range(RUNS)
    ]

    score = answers.count(CORRECT)

    print(f"{model:<15} {score}/{RUNS} {answers}")
