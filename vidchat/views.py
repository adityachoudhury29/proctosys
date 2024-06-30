from datetime import datetime
import json
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.http import HttpResponseRedirect, JsonResponse
from agora_token_builder import RtcTokenBuilder
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from .models import *
from proctor.models import *
import random, time
from django.conf import settings

@login_required
def getToken(request):
    appId = settings.APP_ID
    appCertificate = settings.APP_CERTIFICATE
    channelName = request.GET.get('channel')
    uid = random.randint(1,230)
    expirationTimeInSeconds = 3600*24
    currentTimeStamp = time.time()
    privilegeExpiredTs = currentTimeStamp + expirationTimeInSeconds
    role=1
    token = RtcTokenBuilder.buildTokenWithUid(appId, appCertificate, channelName, uid, role, privilegeExpiredTs)
    return JsonResponse({'token':token,'uid':uid},safe=False)

@login_required
def examroom(request,id):
    allexams=Exam.objects.all()
    for i in allexams:
        if i.end_time<timezone.now():
            i.status=True
            i.save()
    exam=Exam.objects.get(pk=id)
    if request.user == exam.student or request.user == exam.proctor:
        myprof=Profile.objects.get(profile=request.user)
        if exam.status==False:
            return render(request, "vidchat/examroom.html",{
                "exam":exam,
                "myprof":myprof
            })

@never_cache
@login_required
def start(request,id):
    allexams=Exam.objects.all()
    for i in allexams:
        if i.end_time<timezone.now():
            i.status=True
            i.save()
    exam=Exam.objects.get(pk=id)
    current_time = timezone.now()
    start_time = exam.start_time
    # print(current_time)
    # print(start_time)
    if current_time >= start_time:
        if request.user == exam.student or request.user == exam.proctor:
            myprof=Profile.objects.get(profile=request.user)
            try:
                roomname=room.objects.get(name=f"{id}")
            except ObjectDoesNotExist:
                roomname=room(name=f"{id}")
                roomname.save()
            chats=messages.objects.filter(roomname=roomname)
            if myprof.role == "student":
                otherprof=Profile.objects.get(profile=exam.proctor)
            else:
                otherprof=Profile.objects.get(profile=exam.student)
            current_time = time.time()
            start_time = time.mktime(exam.start_time.timetuple())
            duration_seconds = exam.duration * 60
            time_left = start_time + duration_seconds - current_time
            if exam.status==False:
                return render(request, "vidchat/inexam.html",{
                    "room":roomname.name,
                    "chats":chats,
                    "exam":exam,
                    "questions":exam.questions.all(),
                    "myprofile":myprof,
                    "otherprofile":otherprof,
                    "time_left":time_left
                })
            else:
                return render(request,"proctor/404.html")
    else:
        return render(request,"proctor/404.html")

@login_required
def submitexam(request,id):
    exam=Exam.objects.get(pk=id)
    if request.user == exam.student or request.user == exam.proctor:
        questions=exam.questions.all()
        if request.method=="POST":
            for i in questions:
                qa=request.POST.get(f"qa_{i.id}")
                response=Response(user=Profile.objects.get(profile=exam.student),exam=exam,question=i,answer=qa)
                response.save()
            exam.status=True
            exam.save()
            return HttpResponseRedirect(reverse("exam"))

@login_required
def examterminated(request,id):
    exam=Exam.objects.get(pk=id)
    exam.unfair_means=True
    exam.status=True
    exam.save()
    return render(request,"vidchat/examterminated.html")

@never_cache
@login_required
def edit_exam(request,id):
    profile=Profile.objects.get(profile=request.user)
    if profile.role=="admin":
        return render(request,'vidchat/editexam.html',{
            'exam':Exam.objects.get(pk=id)
        })

@login_required
def save_edited_exam(request,id):
    profile=Profile.objects.get(profile=request.user)
    if profile.role=="admin":
        if request.method=='POST':
            exam=Exam.objects.get(pk=id)
            exam.title=request.POST.get('title')
            exam.description=request.POST.get('description')
            start_time=request.POST['start_time']
            end_time=request.POST['end_time']
            student_username=request.POST['student_username']
            exam.student=User.objects.get(username=student_username)
            proctor_username=request.POST['proctor_username']
            exam.proctor=User.objects.get(username=proctor_username)
            exam_date=request.POST['date']
            s_datetime_str = f"{exam_date} {start_time}"
            s_combined_datetime = datetime.strptime(s_datetime_str, '%Y-%m-%d %H:%M')
            e_datetime_str = f"{exam_date} {end_time}"
            e_combined_datetime = datetime.strptime(e_datetime_str, '%Y-%m-%d %H:%M')
            exam.start_time=s_combined_datetime
            exam.end_time=e_combined_datetime
            exam.duration=request.POST.get('duration')
            exam.save()
            return HttpResponseRedirect(reverse('exam'))

@login_required
def delete_exam(request,id):
    profile=Profile.objects.get(profile=request.user)
    if profile.role=="admin":
        exam=Exam.objects.get(pk=id)
        exam.delete()
        return HttpResponseRedirect(reverse('exam'))

@login_required
def exam_page(request,id):
    profile=Profile.objects.get(profile=request.user)
    if profile.role=="admin":
        return render(request,'vidchat/exam_page.html',{
            'exam':Exam.objects.get(pk=id)
        })

@login_required
def edit_q(request,id):
    profile=Profile.objects.get(profile=request.user)
    if profile.role=="admin":
        return render(request,'vidchat/edit_q.html',{
            'exam':Exam.objects.get(pk=id),
            'questions':Exam.objects.get(pk=id).questions.all()
        })
    
@login_required
def save_questions(request,id):
    if request.method == "POST":
        profile = get_object_or_404(Profile, profile=request.user)
        if profile.role == "admin":
            exam = get_object_or_404(Exam, pk=id)
            data = json.loads(request.body)
            questions_data = data.get('questions', [])

            # Clear existing questions
            exam.questions.clear()

            for q_data in questions_data:
                question_text = q_data.get('question')
                answer_text = q_data.get('answer')
                try:
                    question = Question.objects.get(question=question_text, answer=answer_text)
                except ObjectDoesNotExist:
                    question = Question.objects.create(question=question_text, answer=answer_text)

                exam.questions.add(question)
            exam.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'unauthorized'}, status=403)
    return JsonResponse({'status': 'invalid_method'}, status=405)