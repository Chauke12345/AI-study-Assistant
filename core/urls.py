from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('summarize/', views.summarize, name='summarize'),
    path('quiz/', views.quiz, name='quiz'),
    path('quiz-question/', views.quiz_question, name='quiz_question'),
    path('result/', views.result, name='result'),
]