from llm_config import client, MODEL


def translate(word, language):
    message = client.messages.create(
        model=MODEL,
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Translate the word '{word}' into {language}. "
                    "Respond with only the translated word, without "
                    "quotation marks, explanations, or additional text."
                ),
            }
        ],
    )

    return message.content[0].text.strip()


print(translate("hello", "Spanish"))
print(translate("chicken", "Italian"))