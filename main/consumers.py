import json
from channels.generic.websocket import AsyncWebsocketConsumer
import random
import datetime


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
        self.confirmation = 0
        self.state = ""

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

    def isEmpty(self):
        if len(self.room_users) == 0:
            return True

    def confirmations(self):
        return self.confirmation

    def SetPlayerState(self,state):
        self.state = state

    def GetPlayerState(self):
        return self.state      

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
      

        if self.room_group_name not in rooms:
            rooms[self.room_group_name] = Room()
            room = rooms[self.room_group_name]
            room.create_room(self.room_group_name)
        else:
            room = rooms[self.room_group_name]
        
        # Join room group
        await self.channel_layer.group_add(

            self.room_group_name,
            self.channel_name,
        )
        await self.accept()
        # Send message to room group
        await self.send(text_data=json.dumps(room.__dict__))
        await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'action',
                        'action': "give_time"

                    })

            





    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )
        room = rooms[self.room_group_name]
        room.remove_user(self.user.username)
        username = self.user.username
        if len(room.room_users) == 1:
                room.room_host = username[0]

        print("Disconnected: ")
        print(room.room_users)





    # Receive message from WebSocket
    async def receive(self, text_data):
        username = self.user.username.split("_")[0]
        room = rooms[self.room_group_name]
        text_data_json = json.loads(text_data)  
        if 'username' in text_data_json:
            username = self.user.username = text_data_json['username'] +"_"+ str(random.randint(0,1000000))
            room = rooms[self.room_group_name]
            if len(room.room_users) == 1:
                room.room_host = username
            room.add_user(username)
            print("Connected: ")
            print(room.room_users)
            
        


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
        elif 'new_user_time' in text_data_json:
                new_user_time = text_data_json['new_user_time']
                print(str(new_user_time) + " is the time received")
                await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': "NewUserTime",
                    'new_user_time': new_user_time,
                }
            )                
        elif 'action' in text_data_json:
            action = text_data_json['action']
            room = rooms[self.room_group_name]
            if 'data' in text_data_json:
                data = text_data_json['data']
                if action == "play" or action == "pause" or action =="seek":
                        print(self.user.username + "action: " + action + ": " + str(data))
                        if action == "play" or action == "pause":
                            room.SetPlayerState(action)
                        await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'action',
                            'action': action,
                            'data': data,
                            'username': self.user.username,

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
                        'username': self.user.username,

                    }
                )
              
                                                   
            else:
                room.SetPlayerState(action)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'action',
                        'action': action,
                        'username': self.user.username,


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
        if action == "play" or action == "pause":
            if 'current_time' in event:
                print("is this even tried?")
                data = event['current_time']
                username = event['username']
                print("Pause/Play Initiator: " + username)
                if self.user.username != username:
                    await self.send(text_data=json.dumps({
                    'action': action,
                    'current_time': data,
                }))
                
            else:
                username = event['username']
                print("Pause/Play Initiator: " + username)
                if self.user.username != username:
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
                username = event['username']
                print(self.user.username + " seeked time: " + str(data))
                if self.user.username != username:
                    print(self.user.username + " followed time: " + str(data))

                    await self.send(text_data=json.dumps({
                    'action': action,
                    'current_time': data,
                 }))
                
        elif action == "give_time":
            room = rooms[self.room_group_name]
            print("room len: " + str(len(room.room_users)))
            if len(room.room_users) > 0:
                print("last guy: " + room.room_users[-1] + "self: " + self.user.username)
                if self.user.username == room.room_users[0]:
                    await self.send(text_data=json.dumps({
                    'action': "give_time",
                }))

        else:
                # Send message to WebSocket
                await self.send(text_data=json.dumps({
                'action': action,
            }))            
       
            
             

    async def NewUserTime(self, event):
        new_user_time = event['new_user_time']
        print(str(new_user_time) + "is the time for new usesssr")
        # Send message to WebSocket
        room = rooms[self.room_group_name]
        print("user: " + self.user.username + " last_user: " + room.room_users[-1])
        if self.user.username == room.room_users[-1]:
            await self.send(text_data=json.dumps({
            'seekTo': new_user_time,
            'playerstate': room.GetPlayerState()   }))
        if self.user.username != room.room_users[-1]:
            await self.send(text_data=json.dumps({
            'new_user': room.room_users[-1].split("_")[0],}))

        




