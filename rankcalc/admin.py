from django.contrib import admin
from .models import Candidate

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'roll_number', 'exam_date', 'subject', 'total_marks', 'bonus_marks')
    search_fields = ('name', 'roll_number', 'subject')
    list_filter = ('exam_date', 'subject')
