from django.db import IntegrityError
import calendar
from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
import json
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from .models import Profile, User, Question, Exam, Response
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

def handler404(request, exception):
    return render(request, 'proctor/404.html', status=404)

@never_cache
def index(request):
    if request.user.is_authenticated:
        profile=Profile.objects.get(profile=request.user)
        if profile.role=="proctor":
            return render(request,'proctor/index.html',{
                'profile':profile,
                'exams':Exam.objects.filter(proctor=request.user,status=False)
            })
        elif profile.role=="admin":
            return render(request,'proctor/index.html',{
                'profile':profile,
                'exams':Exam.objects.filter(status=False)
            })
        else:
            return render(request,'proctor/index.html',{
                'profile':profile,
                'exams':Exam.objects.filter(student=request.user,status=False)
            })
    else:
       return render(request,'proctor/index.html')

@never_cache
def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        password = request.POST["password"]
        role = request.POST.get("role")
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "proctor/register.html", {
                "message": "Passwords must match!"
            })
        elif role=="select":
            return render(request, "proctor/register.html", {
                "message": "Please select a role!"
            })
        try:
            if username == "":
                return render(request, "proctor/register.html",{
                    "message": "Username cannot be empty!"
                })
            user = User.objects.create_user(username, email, password)
            user.first_name=first_name
            user.last_name=last_name
            l=[user.first_name,user.last_name,user.password]
            for i in l:
                if i == "" or role=="select":
                    return render(request, "proctor/register.html",{
                        "message": "All non-optional fields are compulsory!"
                    })
                else:
                    continue
            user.save()
            profile=Profile(profile=user,role=role)
            profile.save()
        except IntegrityError:
            return render(request, "proctor/register.html", {
                "message": "Username already taken!"
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "proctor/register.html")
    

@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            profile=Profile.objects.get(profile=user)
            profile.session_key = request.session.session_key
            profile.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "proctor/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "proctor/login.html")
    
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

@never_cache
@login_required
def create_exam(request):
    profile=Profile.objects.get(profile=request.user)
    if request.method=="GET" and profile.role=="admin": 
        return render(request,'proctor/createexam.html')
    else:
        return render(request,'proctor/404.html')

@login_required
def save_exam(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            questions_data = data.get('questions', [])
            exam_data = data.get('exam', {})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
        exam_title=exam_data['title']
        description=exam_data['description']
        duration=int(exam_data['duration'])
        start_time=exam_data['start_time']
        end_time=exam_data['end_time']
        student_username=exam_data['student_username']
        proctor_username=exam_data['proctor_username']
        exam_date=exam_data['exam_date']
        s_datetime_str = f"{exam_date} {start_time}"
        s_combined_datetime = datetime.strptime(s_datetime_str, '%Y-%m-%d %H:%M')
        e_datetime_str = f"{exam_date} {end_time}"
        e_combined_datetime = datetime.strptime(e_datetime_str, '%Y-%m-%d %H:%M')
        
        current_time = datetime.now()
        if s_combined_datetime <= current_time:
            return JsonResponse({'success': False, 'error': 'Start time must be after the current time'}, status=400)
        
        expected_end_time = s_combined_datetime + timedelta(minutes=duration)
        if e_combined_datetime != expected_end_time:
            return JsonResponse({'success': False, 'error': f'End time must be exactly {duration} minutes after the start time'}, status=400)
        
        if len(questions_data) == 0:
            return JsonResponse({'success': False, 'error': 'At least one question is required'}, status=400)

        try:
            student = User.objects.get(username=student_username)
            proctor = User.objects.get(username=proctor_username)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Student not found'}, status=400)
        
        exam=Exam(title=exam_title,description=description,duration=duration,proctor=proctor,student=student,start_time=s_combined_datetime,end_time=e_combined_datetime)
        exam.save()
        for question_data in questions_data:
            question_text = question_data.get('question')
            answer_text = question_data.get('answer')
            if not question_text:
                continue
            question = Question(question=question_text,answer=answer_text)  # Create new question instance
            question.save()
            exam.questions.add(question)
        exam.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@login_required  
def exam(request):
    profile=Profile.objects.get(profile=request.user)
    allexams=Exam.objects.all()
    for i in allexams:
        if i.end_time<timezone.now():
            i.status=True
            i.save()
    if profile.role=="proctor":
        return render(request,'vidchat/exam.html',{
            'exams':Exam.objects.filter(proctor=request.user,status=False),
            'profile':profile,
        })
    elif profile.role=="student":
        return render(request,'vidchat/exam.html',{
            'exams':Exam.objects.filter(student=request.user,status=False),
            'profile':profile,
        })
    else:
        return render(request,'vidchat/exam.html',{
            'exams':Exam.objects.filter(status=False),
            'profile':profile,
        })

def evaluate_exam(id):
    exam=Exam.objects.get(pk=id)
    questions=exam.questions.all()
    responses=Response.objects.filter(exam=exam)
    score=0
    for response in responses:
        for question in questions:
            if response.question==question:
                if response.answer.strip().lower()==question.answer.strip().lower():
                    score+=1
    return score

@login_required
def evaluate(request,id):
    profile = Profile.objects.get(profile=request.user)
    if profile.role=="student" or profile.role=="admin":
        exam=Exam.objects.get(pk=id)
        score=evaluate_exam(id)
        responses=Response.objects.filter(exam=exam)
        if len(responses)==0:
            return render(request,'proctor/evaluate.html',{
                'exam':exam,
                'score':score,
                'total':exam.questions.count(),
                'message':'No responses found!'
            })
        return render(request,'proctor/evaluate.html',{
            'exam':exam,
            'score':score,
            'total':exam.questions.count(),
            'responses':responses
        })

@login_required
def evaluations(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(profile=request.user)
        if profile.role == 'student' or profile.role == 'admin':
            return render(request,'proctor/evaluations.html',{
                'ev_exams':Exam.objects.filter(student=request.user,status=True,unfair_means=False),
                'term_exams':Exam.objects.filter(student=request.user,status=True,unfair_means=True)
            })

@login_required
def ended_exams(request,id):
    if request.user.is_authenticated:
        return render(request,'proctor/exam_terminated.html',{
            'exam':Exam.objects.get(pk=id)
        })

@login_required   
def calendar_view(request):
    current_date = timezone.now()
    today_list = current_date.strftime('%Y-%m-%d').split('-')
    today = int(today_list[2])
    month = current_date.month
    year = current_date.year
    cal = calendar.Calendar()
    year_calendar_data = {}
    exam_dates=[]
    for i in Exam.objects.filter(status=False):
        exam_dates.append(i.start_time.date().strftime('%Y-%m-%d'))

    print(exam_dates)

    for m in range(1, 13):
        month_days = cal.monthdayscalendar(year, m)
        year_calendar_data[m] = month_days

    return render(request, 'proctor/calendar.html', {
        'today': today,
        'current_month': month,
        'current_year': year,
        'year': year,
        'year_calendar': year_calendar_data,
        'exam_dates': exam_dates
    })

@login_required   
def calendar_next_year(request):
    current_date = timezone.now()
    today_list = current_date.strftime('%Y-%m-%d').split('-')
    today = int(today_list[2])
    month = current_date.month
    c_year = current_date.year
    year = c_year+1
    cal = calendar.Calendar()
    year_calendar_data = {}
    exam_dates=[]
    for i in Exam.objects.filter(status=False):
        exam_dates.append(i.start_time.date().strftime('%Y-%m-%d'))

    print(exam_dates)

    for m in range(1, 13):
        month_days = cal.monthdayscalendar(year, m)
        year_calendar_data[m] = month_days

    return render(request, 'proctor/calendar.html', {
        'today': today,
        'current_month': month,
        'current_year': c_year,
        'year': year,
        'year_calendar': year_calendar_data,
        'exam_dates': exam_dates
    })


@login_required
def date_exam(request,date):
    exams=Exam.objects.filter(start_time__date=date)
    if len(exams)>0:
        return render(request,'proctor/date_exam.html',{
            'exams':exams,
            'date':date,
        })
    else:
        return render(request,'proctor/date_exam.html',{
            'message':'You have no exams scheduled on this date!',
            'date':date,
        })
    
@login_required
def report(request):
    profile = Profile.objects.get(profile=request.user)
    if profile.role == "student":
        exams=Exam.objects.filter(status=True,student=request.user)
        return render(request,'proctor/report.html',{
            'exams':exams
        })