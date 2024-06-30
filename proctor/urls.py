from django.contrib import admin
from django.urls import path
from .views import *

#app_name = 'proctor'

urlpatterns = [
    path('',index,name='index'),
    path('login/',login_view,name='login'),
    path('register/',register,name='register'),
    path('logout/',logout_view,name='logout'),
    path('createexam/',create_exam,name='create_exam'),
    path('save_exam/',save_exam,name='save_exam'),
    path('evaluate/<int:id>',evaluate,name='evaluate'),
    path('evaluations/',evaluations,name='evaluations'),
    path('exam_terminated/<int:id>',ended_exams,name='exam_ended'),
    path('calendar',calendar_view,name='calendar'),
    path('date_exam/<str:date>',date_exam,name='date_exam'),
    path('calendar_next/',calendar_next_year,name='calendar_next_year'),
    path('report/',report,name='report'),
]