def generate_quiz(text: str):
    FALLBACK = {
        "questions": [
            {
                "question": "AI failed to generate quiz. Try again.",
                "options": ["A", "B", "C", "D"],
                "answer": "A"
            }
        ]
    }

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": QUIZ_PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0.2,
        )

        content = response.choices[0].message.content
        data = extract_json(content)

        if not data or "questions" not in data:
            return FALLBACK

        clean_questions = []

        for q in data["questions"]:
            if not isinstance(q, dict):
                continue

            question = q.get("question")
            options = q.get("options")
            answer = q.get("answer")

            if not question or not isinstance(options, list) or not answer:
                continue

            if len(options) != 4:
                continue

            if answer not in options:
                continue

            clean_questions.append({
                "question": question,
                "options": options,
                "answer": answer
            })

        if not clean_questions:
            return FALLBACK

        return {"questions": clean_questions}

    except Exception as e:
        return {
            "questions": [
                {
                    "question": f"System error: {str(e)}",
                    "options": ["A", "B", "C", "D"],
                    "answer": "A"
                }
            ]
        }