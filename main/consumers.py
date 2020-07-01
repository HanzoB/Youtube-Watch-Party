import json
from channels.generic.websocket import AsyncWebsocketConsumer
import random


class UnassignedConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['unassigned']
        self.room_group_name = 'unassigned_%s' % self.room_name
        self.user = self.scope['user']
        # Join room group

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room']
        self.room_group_name = 'room_%s' % self.room_name
        self.user = self.scope['user']
        self.user.username = "User_" + str(random.randint(0, 100000))


        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,

        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if 'message' in text_data_json:
            message = text_data_json['message']
            username = self.user.username
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat',
                    'message': message,
                    "username": username,

                }
            )
        elif 'action' in text_data_json:
            action = text_data_json['action']
            data = text_data_json['data']

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'action',
                    'action': action,
                    'data': data,

                }
            )







    # Receive message from room group
    async def chat(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message,
            "username": event["username"],

        }))



    async def action(self, event):
        action = event['action']
        data = event['data']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'action': action,
            'data': data,
        }))



