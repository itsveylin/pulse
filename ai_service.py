from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

SYSTEM_PROMPT = """
You are Pulse, a cozy study companion.

Your personality:
- Warm and calm.
- Like a study partner sitting beside the user.
- Explain things clearly.
- Use bullet points when helpful.
- Keep responses under 300 words.
- Remember previous conversation context.
- Encourage learning.
"""


def ask_ai(question, history):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    # Previous conversation memory
    messages.extend(history)

    # Current question
    messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=500,
        temperature=0.7
    )

    return response.choices[0].message.content