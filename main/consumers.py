import json
from channels.generic.websocket import AsyncWebsocketConsumer
import random
import datetime
import requests
from .room import Room


# {roomid:{'host':'first user in room';,room_users:[],'current_video': '' ,playlist:[]}}
rooms = {}



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
                    'type': 'usersCount',
                    'action': "users_count",})
        await self.send(text_data=json.dumps(room.__dict__))
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )
       
        

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
                'type': 'giveTime',
                'action': "give_time",

            })
            await self.channel_layer.group_send(
            self.room_group_name,
                {
                    'type': 'usersCount',
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
                    if action == "play" or action == "pause":
                        room.SetPlayerState(action)
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'playerStateChange',
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
                            'type': 'addToPlaylist',
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
                            'type': 'removeFromPlaylist',
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
                            'type': 'loadVideo',
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
                            'type': 'playerStateChange',
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
            'info': "user_message"

        }))



    async def NewUserTime(self, event):
        new_user_time = event['new_user_time']

        # Send message to WebSocket
        room = rooms[self.room_group_name]
        if self.user.username == room.room_users[-1]:
            print("sending playlist")
            await self.send(text_data=json.dumps({
                'seekTo': new_user_time,
                'playerstate': room.GetPlayerState(),
                'info': "new_user_details"}))

        if self.user.username != room.room_users[-1]:
            await self.send(text_data=json.dumps({
                'new_user': room.room_users[-1].split("_")[0],
                'info': "new_user", }))


    async def playerStateChange(self,event):
        action = event["action"]
        username = event['username']

        if action == "seek" and self.user.username != username:
            data = event['data']
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

            
    async def addToPlaylist(self,event):
        room = rooms[self.room_group_name]
        username = event['username']
        video_id = event['video_id']
        title = event['title']
        index = event['index']
        action = event['action']
            
        print(room.playlist)
        await self.send(text_data=json.dumps({
            'action': action,
            'video': [video_id,title],
            "index": index,
            'username':username,
        }))


    async def removeFromPlaylist(self, event):
        username = event['username']
        room = rooms[self.room_group_name]
        await self.send(text_data=json.dumps({
                'action': "removeFromPlaylist",
                'playlistupdate': room.playlist,
                'username':username,
            }))


    async def loadVideo(self,event):
        data = event['data']
        username = event['username']
        action = event['action']
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

    async def usersCount(self,event):
        room = rooms[self.room_group_name]
        await self.send(text_data=json.dumps({
                'room_users': room.room_users,
                'info': "room_users",
            }))

    async def giveTime(self,event):
        room = rooms[self.room_group_name]
        if self.user.username == room.room_users[0]:
            await self.send(text_data=json.dumps({
                'action': "give_time",
            }))



