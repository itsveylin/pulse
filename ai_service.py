from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

SYSTEM_PROMPT = """
<<<<<<< HEAD
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


=======
You are Pulse, a helpful study companion.

Remember previous conversation context.
Keep responses concise.
"""

>>>>>>> 690426bfecb126a1fc0e26a55a879fbbd4fcdff4
def ask_ai(question, history):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

<<<<<<< HEAD
    # Previous conversation memory
    messages.extend(history)

    # Current question
    messages.append(
        {
            "role": "user",
            "content": question
        }
    )
=======
    messages.extend(history)

    messages.append({
        "role": "user",
        "content": question
    })
>>>>>>> 690426bfecb126a1fc0e26a55a879fbbd4fcdff4

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
<<<<<<< HEAD
        max_tokens=500,
        temperature=0.7
=======
        max_tokens=500
>>>>>>> 690426bfecb126a1fc0e26a55a879fbbd4fcdff4
    )

    return response.choices[0].message.content