from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    profile=models.ForeignKey(User,on_delete=models.CASCADE,blank=True,related_name='student')
    session_key = models.CharField(max_length=40, null=True, blank=True)
    CHOICES = [
        ('student', 'student'),
        ('proctor', 'proctor'),
        ('admin', 'admin')
    ]
    role=models.CharField(max_length=50,choices=CHOICES)

    def __str__(self):
        return f"{self.profile.username}:{self.role}"
    
class Exam(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration of exam in minutes")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    proctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proctored_exams')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_exams')
    questions = models.ManyToManyField('Question', related_name='exams')
    status = models.BooleanField(default=False)
    unfair_means = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.title}: {self.proctor.username} -> {self.student.username}"
    def save(self, *args, **kwargs):
        if self.pk:
            current_exam = Exam.objects.get(pk=self.pk)
            if current_exam.status and not self.status:
                Response.objects.filter(exam=current_exam).delete()
        super(Exam, self).save(*args, **kwargs)

class Question(models.Model):
    question = models.CharField(max_length=1000)
    answer = models.CharField(max_length=1000)

    def __str__(self):
        return f"{self.question}"
    
class Response(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='user_response')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_response')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='question_response')
    answer = models.CharField(max_length=1000)

    def __str__(self):
        return f"Response of {self.user.profile.username} on question: {self.question}; in exam: {self.exam.title}"