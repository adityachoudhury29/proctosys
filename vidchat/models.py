from django.db import models
from proctor.models import User

# Create your models here.
class room(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"exam-{self.name}"

class messages(models.Model):
    roomname = models.ForeignKey(room,on_delete=models.CASCADE,related_name='roomname')
    sender=models.ForeignKey(User,related_name='sender',on_delete=models.CASCADE,blank=True)
    content=models.TextField()

    def __str__(self):
        return f'{self.sender.username} in exam-{self.roomname} : {self.content}'
