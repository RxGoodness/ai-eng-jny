from llm_config import client, MODEL
import anthropic

history = []

while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        print("Bye!")
        break

    history.append({"role": "user", "content": user_input})
    try:
        response = client.messages.create(model=MODEL, max_tokens=500, messages=history)
        reply = response.content[0].text
        print(f"Bot: {reply}")
        history.append({"role": "assistant", "content": reply})
        print(f"  (tokens in: {response.usage.input_tokens}, history: {len(history)} msgs)")

    except anthropic.APIConnectionError:
        print("Can't reach the model server. Is Ollama running?")
    except anthropic.NotFoundError:
        print(f"Model '{MODEL}' not found. Check the name / run `ollama list`.")
    except anthropic.APIStatusError as e:
        print(f"API error {e.status_code}: {e.message}")

    print(f"  (tokens in: {response.usage.input_tokens}, history: {len(history)} msgs)")
