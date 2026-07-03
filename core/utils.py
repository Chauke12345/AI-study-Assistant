def safe_fallback(error=None, raw=None):
    return {
        "questions": [
            {
                "question": "System temporarily unavailable.",
                "options": ["A", "B", "C", "D"],
                "answer": "A"
            }
        ]
    }