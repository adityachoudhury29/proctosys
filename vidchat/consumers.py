import json
from django.http import request
from channels.db import database_sync_to_async # type: ignore
from channels.generic.websocket import AsyncWebsocketConsumer # type: ignore
from .models import *
from proctor.models import Profile, User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        uname=text_data_json["username"]
        end=text_data_json["end"]
        user=await database_sync_to_async(User.objects.get)(username=uname)
        room1 = await database_sync_to_async(room.objects.get)(name=self.room_name)

        chat=messages(content=message,sender=user,roomname=room1)
        await database_sync_to_async(chat.save)()
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message, "username":user.username, "end":end}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]
        end = event["end"]

        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "username": username,
                    "end": end
                }
            )
        )