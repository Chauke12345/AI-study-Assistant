import os
import json
import re

from dotenv import load_dotenv
from groq import Groq
from django.shortcuts import render, redirect

from .models import Quiz

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"


# -------------------------
# HOME
# -------------------------
def home(request):
    return render(request, "core/home.html")


# -------------------------
# QUIZ START
# -------------------------
def quiz(request):
    if request.method == "POST":
        text = request.POST.get("text", "").strip()

        if not text:
            return render(request, "core/quiz.html", {
                "error": "Please enter text to generate a quiz."
            })

        quiz_data = generate_quiz(text)

        if not quiz_data or not quiz_data.get("questions"):
            return render(request, "core/quiz.html", {
                "error": "AI returned no valid questions."
            })

        # Save
        Quiz.objects.create(text=text, data=quiz_data)

        # Session init
        request.session["quiz"] = quiz_data
        request.session["score"] = 0
        request.session["index"] = 0

        return redirect("quiz_question")

    return render(request, "core/quiz.html")


# -------------------------
# QUIZ QUESTION FLOW
# -------------------------
def quiz_question(request):
    quiz = request.session.get("quiz")
    index = request.session.get("index", 0)
    score = request.session.get("score", 0)

    if not quiz:
        return redirect("result")

    questions = quiz.get("questions", [])

    if index >= len(questions):
        return redirect("result")

    q = questions[index]

    if request.method == "POST":
        selected = request.POST.get("answer")

        if selected == q.get("answer"):
            score += 1

        request.session["score"] = score
        request.session["index"] = index + 1

        return redirect("quiz_question")

    return render(request, "core/quiz_game.html", {
        "question": q,
        "index": index + 1,
        "total": len(questions)
    })


# -------------------------
# RESULT
# -------------------------
def result(request):
    score = request.session.get("score", 0)
    quiz = request.session.get("quiz", {})

    total = len(quiz.get("questions", []))

    return render(request, "core/result.html", {
        "score": score,
        "total": total
    })


# -------------------------
# SUMMARIZE (simple fallback)
# -------------------------
def summarize(request):
    text = ""
    summary = ""

    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        summary = text[:150] + "..." if text else ""

    return render(request, "core/summarize.html", {
        "text": text,
        "summary": summary
    })


# -------------------------
# AI QUIZ GENERATION
# -------------------------
def generate_quiz(text):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Return ONLY valid JSON.\n\n"
                        "{\n"
                        '  "questions": [\n'
                        "    {\n"
                        '      "question": "string",\n'
                        '      "options": ["A", "B", "C", "D"],\n'
                        '      "answer": "A"\n'
                        "    }\n"
                        "  ]\n"
                        "}\n\n"
                        "Rules:\n"
                        "- Exactly 5 questions\n"
                        "- No markdown\n"
                        "- No explanations"
                    )
                },
                {"role": "user", "content": text}
            ],
            temperature=0.2
        )

        raw = response.choices[0].message.content
        data = extract_json(raw)

        if not data or not isinstance(data.get("questions"), list):
            return {"questions": []}

        clean = []

        for q in data["questions"]:
            if not isinstance(q, dict):
                continue

            question = q.get("question")
            options = q.get("options")
            answer = q.get("answer")

            if question and options and answer:
                clean.append({
                    "question": question,
                    "options": options,
                    "answer": answer
                })

        return {"questions": clean}

    except Exception as e:
        print("AI ERROR:", e)
        return {"questions": []}


# -------------------------
# JSON PARSER
# -------------------------
def extract_json(text):
    if not text:
        return None

    try:
        return json.loads(text)
    except:
        pass

    cleaned = re.sub(r"```json|```", "", text).strip()

    try:
        return json.loads(cleaned)
    except:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}") + 1

    try:
        return json.loads(cleaned[start:end])
    except:
        return None