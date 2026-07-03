from django.db import models

class Quiz(models.Model):
    text = models.TextField()
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)