from django.contrib import admin
from .models import Profile, Exam, Question, Response

admin.site.register(Profile)
admin.site.register(Exam)
admin.site.register(Question)
admin.site.register(Response)