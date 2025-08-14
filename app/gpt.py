import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "You are a polite telephone assistant.")

def ask_gpt(messages):
    completion = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            *messages
        ]
    )
    return completion.choices[0].message["content"]
