import json
from channels.generic.websocket import AsyncWebsocketConsumer
import random


#{roomid:{'host':'first user in room';,room_users:[],'current_video': '' ,playlist:[]}}
rooms = {}

class Room:

    def __init__(self):
        self.room_id = ''
        self.room_host = ''
        self.room_users = []
        self.curr_video = ''
        self.playlist = []

    def create_room(self, room_id):
        self.room_id = room_id

    def add_user(self, user):
        self.room_users += [user]

    def remove_user(self, user):
        self.room_users -= [user]
        if len(room_users) == 0

    def room_host(self, host):
        if self.room_host == '':
            self.room_host = host
        else:
            return "Host exists"

    def add_to_playlist(self, video_id):
        self.playlist += [video_id]

    def remove_from_playlist(self, video_id):
        self.playlist -= [video_id]

    def room_info(self):
        return "Room_ID: %s \n Room_host: %s \n room_users: %s "%(self.room_id, self.room_host, self.room_users)







class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room']
        self.room_group_name = 'room_%s' % self.room_name
        self.user = self.scope['user']
        username = self.user.username = "User_" + str(random.randint(0, 100000))

        if self.room_group_name not in rooms:
            rooms[self.room_group_name] = Room()
            room = rooms[self.room_group_name]
            room.create_room(self.room_group_name)
        else:
            room = rooms[self.room_group_name]
        if room.room_host == '':
            room.room_host = username
        if username not in room.room_users:
            room.add_user(username)
        print(room.room_users)



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
        username = self.user.username
        text_data_json = json.loads(text_data)
        if 'message' in text_data_json:
            print("eceive(self, text_data)")
            message = text_data_json['message']
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
        elif 'new_user' in text_data_json:
            new_user = text_data_json['new_user']
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'notification',
                    'new_user': new_user,
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

    async def notification(self, event):
        print("called")
        new_user = event['new_user']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'new_user': new_user,
        }))



