from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

SYSTEM_PROMPT = """
You are Pulse, a helpful study companion for students.

Rules:
- Keep answers under 300 words.
- Use bullet points when possible.
- Give practical advice.
- Explain technical topics simply.
- Avoid extremely long answers.
"""

def ask_ai(question):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": question
            }
        ],
        max_tokens=500
    )

    return response.choices[0].message.content