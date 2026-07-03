import json
from django.shortcuts import render, redirect
from .ai_service import generate_quiz
from .models import Quiz


# -------------------------
# HOME
# -------------------------
def home(request):
    return render(request, "core/home.html")


# -------------------------
# QUIZ START (GENERATE)
# -------------------------
def quiz(request):
    if request.method == "POST":
        text = request.POST.get("text")

        quiz_data = generate_quiz(text)

        if not quiz_data or "error" in quiz_data:
            return render(request, "core/quiz.html", {
                "error": "AI failed to generate quiz. Try again."
            })

        # SAVE TO DB (optional but correct)
        Quiz.objects.create(
            text=text,
            data=quiz_data
        )

        # STORE IN SESSION
        request.session["quiz"] = quiz_data
        request.session["score"] = 0
        request.session["index"] = 0

        return redirect("quiz_question")

    return render(request, "core/quiz.html")


# -------------------------
# QUIZ QUESTIONS
# -------------------------
def quiz_question(request):
    quiz = request.session.get("quiz")
    index = request.session.get("index", 0)
    score = request.session.get("score", 0)

    if not quiz or index >= len(quiz["questions"]):
        return redirect("result")

    q = quiz["questions"][index]

    if request.method == "POST":
        selected = request.POST.get("answer")

        if selected == q["answer"]:
            score += 1

        request.session["score"] = score
        request.session["index"] = index + 1

        return redirect("quiz_question")

    return render(request, "core/quiz_game.html", {
        "question": q,
        "index": index + 1,
        "total": len(quiz["questions"])
    })


# -------------------------
# RESULT
# -------------------------
def result(request):
    score = request.session.get("score", 0)
    quiz = request.session.get("quiz")

    total = len(quiz["questions"]) if quiz else 0

    return render(request, "core/result.html", {
        "score": score,
        "total": total
    })


# -------------------------
# SAFE FALLBACK
# -------------------------
def safe_fallback(error=None, raw=None):
    return {
        "questions": [
            {
                "question": "System temporarily unavailable.",
                "options": ["A", "B", "C", "D"],
                "answer": "A"
            }
        ],
        "status": "fallback"
    }
def summarize(request):
    text = ""
    summary = ""

    if request.method == "POST":
        text = request.POST.get("text")
        summary = text[:150] + "..." if text else ""

    return render(request, "core/summarize.html", {
        "text": text,
        "summary": summary
    })