from django.urls import path
from vidchat import views
import proctor

urlpatterns=[
    path("", proctor.views.exam, name="exam"),
    path("room/<int:id>", views.examroom, name="room"),
    path("room/<int:id>/start", views.start, name="start"),
    path("gettoken/", views.getToken, name="getToken"),
    path("submitexam/<int:id>", views.submitexam, name="submit"),
    path("examterminated/<int:id>", views.examterminated, name="examterminated"),
    path('editexam/<int:id>',views.edit_exam,name='edit'),
    path('save_edit/<int:id>',views.save_edited_exam,name='save_edited_exam'),
    path('delete_exam/<int:id>',views.delete_exam,name='delete_exam'),
    path('exam_page/<int:id>',views.exam_page,name='exam_page'),
    path('edit-q/<int:id>',views.edit_q,name='edit_q'),
    path('save-questions/<int:id>', views.save_questions, name='save_questions'),
]