import json
import os
from groq import Groq

# -------------------------
# Safe client init
# -------------------------
api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key) if api_key else None

if client is None:
    print("⚠️ GROQ_API_KEY missing")


# -------------------------
# Prompt
# -------------------------
QUIZ_PROMPT = """
Return ONLY valid JSON quiz with 5 questions.

RULES:
- Exactly 5 questions
- Each question has 4 options (A, B, C, D)
- Only ONE correct answer
- Answer must be A, B, C or D
- No explanations
"""


# -------------------------
# Main function
# -------------------------
def generate_quiz(text):

    if client is None:
        return {"error": "API key missing"}

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": QUIZ_PROMPT},
            {"role": "user", "content": text}
        ]
    )

    content = response.choices[0].message.content

    if not content:
        return {"error": "Empty response"}

    print("AI RAW OUTPUT:", content)

    try:
        return json.loads(content)
    except Exception:
        return {"error": "Invalid JSON", "raw": content}