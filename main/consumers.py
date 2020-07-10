import json
from channels.generic.websocket import AsyncWebsocketConsumer
import random
import time


#{roomid:{'host':'first user in room';,room_users:[],'current_video': '' ,playlist:[]}}
rooms = {}


class Room:

    def __init__(self):
        self.room_id = ''
        self.room_host = ''
        self.room_users = []
        self.current_video = ''
        self.playlist = []
        self.current_time = 0

    def curr_video(self, video):
        self.current_video = video
        print("Current Video: " + video)
    
    def curr_time(self,time):
        self.current_time = time
        print(time)

    def create_room(self, room_id):
        self.room_id = room_id

    def add_user(self, user):
        self.room_users.append(user)

    def remove_user(self, user):
        self.room_users.remove(user)

    def is_empty(self):
        if len(self.room_users) == 0:
            return True

    def room_host(self, host):
        if self.room_host == '':
            self.room_host = host
        else:
            return "Host exists"

    def add_to_playlist(self, video_id):
        self.playlist.append(video_id)

    def remove_from_playlist(self, video_id):
        self.playlist.remove(video_id)

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
        # Send message to room group
        username = self.user.username
        await self.send(text_data=json.dumps(room.__dict__))
        print(json.dumps(room.__dict__))
            





    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )
        room = rooms[self.room_group_name]
        room.remove_user(self.user.username)


        print(room.room_users)
        print(rooms)





    # Receive message from WebSocket
    async def receive(self, text_data):
        username = self.user.username
        room = rooms[self.room_group_name]
        text_data_json = json.loads(text_data)
        if 'message' in text_data_json:
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
            if 'data' in text_data_json:
                data = text_data_json['data']
                if action == "play" or action == "pause" or action =="seek":
                        print("seekit: " + str(data))
                        await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'action',
                            'action': action,
                            'data': data,

                        }
                    )
                else:
                    room.curr_video(data)
                    await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'action',
                        'action': action,
                        'data': data,

                    }
                )                                        
            else:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'action',
                        'action': action,

                    }
                )
                










    # Receive message from room group
    async def chat(self, event):
        message = event['message']
        print(message)
        await self.send(text_data=json.dumps({
            'message': message,
            "username": event["username"],

        }))

    async def action(self, event):
        action = event['action']
        if action == "play" or action == "pause":
            if 'current_time' in event:
                print("is this even tried?")
                data = event['current_time']
                await self.send(text_data=json.dumps({
                'action': action,
                'current_time': data,
            }))
            else:
                await self.send(text_data=json.dumps({
                'action': action,
            })) 

        elif action == "load_video":
                data = event['data']
                print("second3" + data)
                await self.send(text_data=json.dumps({
                'action': action,
                'data': data,
            }))
        elif action == "seek":

                data = event['data']
                print("the seeked time: " + str(data))
                await self.send(text_data=json.dumps({
                'action': action,
                'current_time': data,
            }))

        else:
                # Send message to WebSocket
                await self.send(text_data=json.dumps({
                'action': action,
            }))            
       
            
            

       
             
    async def notification(self, event):
        new_user = event['new_user']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'new_user': new_user,
        }))



