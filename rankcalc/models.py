from django.db import models

class Candidate(models.Model):
    roll_number = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    exam_date = models.CharField(max_length=20)
    exam_time = models.CharField(max_length=20)
    venue = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    total_marks = models.FloatField()
    bonus_marks = models.FloatField()
    bonus_questions = models.TextField()
    answer_key_link = models.URLField()

    def __str__(self):
        return f"{self.roll_number} - {self.name}"
