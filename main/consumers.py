import json
from channels.generic.websocket import AsyncWebsocketConsumer
import random
import datetime
import requests




# {roomid:{'host':'first user in room';,room_users:[],'current_video': '' ,playlist:[]}}
rooms = {}


#room.py
class Room:

    def __init__(self):
        self.room_id = ''
        self.room_host = ''
        self.room_users = []
        self.current_video = 'HLEn5MyXUfE'
        self.playlist = []
        self.current_time = 0
        self.confirmation = 0
        self.state = ""
        self.index = 1

    def curr_video(self, video):
        self.current_video = video
        print("Current Video: " + video)

    def curr_time(self, time):
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

    def SetPlayerState(self, state):
        self.state = state

    def GetPlayerState(self):
        return self.state

    def room_host(self, host):
        if self.room_host == '':
            self.room_host = host
        else:
            return "Host exists"

    def add_to_playlist(self, videoID):
        self.playlist.append(videoID)
        print("append")

    def remove_from_playlist(self, videoID, index):
        for i in range(len(self.playlist)):
            if self.playlist[i]['video_id']  == videoID.split("_")[1] and str(self.playlist[i]['index']) == videoID.split("_")[2]:

                del self.playlist[i]
                print(self.playlist)
                    
                break
                
                
            
           

    def room_info(self):
        room_info = {"id":self.room_id,"host":self.host,"room_users":self.room_users}
        return room_info


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
        
         

    async def disconnect(self, close_code):
        # Leave room group
        room = rooms[self.room_group_name]
        room.remove_user(self.user.username) 
        await self.channel_layer.group_send(
            self.room_group_name,
                {
                    'type': 'action',
                    'action': "users_count",})
        await self.send(text_data=json.dumps(room.__dict__))
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )
       
        

       

    # Receive message from WebSocket

    async def receive(self, text_data):
        username = self.user.username.split("_")[0]
        room = rooms[self.room_group_name]
        text_data_json = json.loads(text_data)
        if 'username' in text_data_json:
            username = self.user.username = text_data_json['username'] + "_" + str(
                random.randint(0, 1000000))
            room = rooms[self.room_group_name]
            if len(room.room_users) == 0:
                room.room_host = username
            room.add_user(username)
            print(room.room_users)
            await self.send(text_data=json.dumps(room.__dict__))
            await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'action',
                'action': "give_time",

            })
            await self.channel_layer.group_send(
            self.room_group_name,
                {
                    'type': 'action',
                    'action': "users_count",}) 

        elif 'message' in text_data_json:
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
                if action == "play" or action == "pause" or action == "seek":
                    print(self.user.username + "action: " +
                          action + ": " + str(data))
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
                elif action =="addToPlaylist":
                    print("added to playlist by: " + self.user.username)
                    response = requests.get('http://noembed.com/embed?url=https://www.youtube.com/watch?v=' + data ) 
                    title = response.json()['title']
                    room.index += 1
                    room.add_to_playlist({"video_id":data, "title":title, "index": room.index})
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'action',
                            'action': action,
                            'video_id': data,
                            'title':title,
                            'index': room.index,
                            'username': self.user.username, 


                        }
                    )
                elif  action =="removeVideoPlaylist":
                    room.remove_from_playlist(data,data.split("_")[2])
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
                if action == "pause" or action == "play":
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
        room = rooms[self.room_group_name]
        if action == "play" or action == "pause":
            if 'current_time' in event:
                data = event['current_time']
                username = event['username']
                if self.user.username != username:
                    await self.send(text_data=json.dumps({
                        'action': action,
                        'current_time': data,
                    }))

            else:
                username = event['username']
                if self.user.username != username:
                    await self.send(text_data=json.dumps({
                        'action': action,
                        'username' : username.split("_")[0],
                    }))

        elif action == "load_video":
            data = event['data']
            username = event['username']
            if self.user.username != username:
                print("sent to " + self.user.username)
                await self.send(text_data=json.dumps({
                'action': action,
                'data': data,
                'username' : username.split("_")[0],
            }))
            else:
                await self.send(text_data=json.dumps({
                'action': action,
                'username' : username.split("_")[0],
            }))
        elif action == "addToPlaylist":
            username = event['username']
            video_id = event['video_id']
            title = event['title']
            index = event['index']
            
            print(room.playlist)
            await self.send(text_data=json.dumps({
                'action': action,
                'video': [video_id,title],
                "index": index,
                'username':username,
            }))
            
        elif action =="removeVideoPlaylist":
            username = event['username']
            await self.send(text_data=json.dumps({
                    'action': "removeFromPlaylist",
                    'playlistupdate': room.playlist,
                    'username':username,
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
            if len(room.room_users) > 0:
                print("last guy: " +
                      room.room_users[-1] + "self: " + self.user.username)
                if self.user.username == room.room_users[0]:
                    await self.send(text_data=json.dumps({
                        'action': "give_time",
                    }))
        elif action == "users_count":
            room = rooms[self.room_group_name]
            await self.send(text_data=json.dumps({
                    'room_users': room.room_users,
                }))
                

        else:
                # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'action': action,
            }))

    async def NewUserTime(self, event):
        new_user_time = event['new_user_time']

        # Send message to WebSocket
        room = rooms[self.room_group_name]
        if self.user.username == room.room_users[-1]:
            print("sending playlist")
            await self.send(text_data=json.dumps({
                'seekTo': new_user_time,
                'playerstate': room.GetPlayerState()}))

        if self.user.username != room.room_users[-1]:
            await self.send(text_data=json.dumps({
                'new_user': room.room_users[-1].split("_")[0], }))
