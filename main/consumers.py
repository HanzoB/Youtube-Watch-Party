import json
from channels.generic.websocket import AsyncWebsocketConsumer
import random
import datetime
import requests
from .room import Room
import asyncio


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
                    'type': 'notifyUserDisconnect',
                    'user_disconnect': self.user.username,})
        await self.channel_layer.group_send(
            self.room_group_name,
                {
                    'type': 'usersCountSend',
                    'action': "users_count",})
        await self.send(text_data=json.dumps(room.__dict__))
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )
       
    
    

    #received data from websocket user 
    async def receive(self, text_data):
        room = rooms[self.room_group_name]
        text_data_json = json.loads(text_data)
        try:
            data = text_data_json['data']
            action = text_data_json['action']
        except KeyError:
            pass
             
        async def setUserName(text_data_json):
            username = self.user.username = text_data_json['username'] + "_" + str(
                random.randint(0, 1000000))
            if len(room.room_users) == 0:
                room.room_host = username
            room.add_user(username)
            print(room.room_users)
            await self.send(text_data=json.dumps(room.__dict__))
            await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'giveTimeSend',
                'action': "give_time",

            })
            await self.channel_layer.group_send(
            self.room_group_name,
                {
                    'type': 'usersCountSend',
                    'action': "users_count",}) 
        
        

        async def messageReceive(text_data_json):
            message = text_data_json['message']
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'messageSend',
                    'message': message,
                    "username": self.user.username,
                }
            )

        

        async def NewUserTimeReceive(text_data_json):
            new_user_time = text_data_json['new_user_time']
            await self.channel_layer.group_send(
                self.room_group_name,
                { 
                    'type': "newUserTimeSend",
                    'new_user_time': new_user_time,
                }
            )

        async def addToPlaylistReceive(text_data_json):
                    response = requests.get('http://noembed.com/embed?url=https://www.youtube.com/watch?v=' + data ) 
                    title = response.json()['title']
                    room.index += 1
                    room.add_to_playlist({"video_id":data, "title":title, "index": room.index})
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'addToPlaylistSend',
                            'action': action,
                            'video_id': data,
                            'title':title,
                            'index': room.index,
                            'username': self.user.username, 


                        }
                    )
                    
        async def removeFromPlaylistReceive(text_data_json):
                    room.remove_from_playlist(data,data.split("_")[2])
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'removeFromPlaylistSend',
                            'action': action,
                            'data': data,
                            'username': self.user.username, 


                        }
                    )
        async def loadVideoReceive(text_data_json):
            action = text_data_json['action']
            data = text_data_json['data']
            room.curr_video(data)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'loadVideoSend',
                    'action': action,
                    'data': data,
                     'username': self.user.username,

                })

        async def playerStateChangeReceive(text_data_json):
            action = text_data_json['action']
            room = rooms[self.room_group_name]
            if action == "seek":
                    data = text_data_json['data']
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'playerStateChangeSend',
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
                            'type': 'playerStateChangeSend',
                            'action': action,
                            'username': self.user.username,


                        }
                    )

        
        received = {"username" : setUserName, "message" : messageReceive, 
        'new_user_time': NewUserTimeReceive,'addToPlaylist':addToPlaylistReceive,
        'removeFromPlaylist':removeFromPlaylistReceive, 'loadVideo' : loadVideoReceive, 
        'play':playerStateChangeReceive, 'pause':playerStateChangeReceive, "seek":playerStateChangeReceive}
        await received.get(text_data_json['info'])(text_data_json) 
 
    
                
               




#Sending Received Websocket data to users
    async def messageSend(self, event):
        message = event['message']
        username = event["username"]
        if len(message) > 0:
            await self.send(text_data=json.dumps({
            'message': message,
            "username": username.split("_")[0],
            'info': "user_message"

        }))


    async def newUserTimeSend(self, event):
        room = rooms[self.room_group_name]
        new_user_time = event['new_user_time']
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

    async def notifyUserDisconnect(self,event):
        user  = event['user_disconnect']
        await self.send(text_data=json.dumps({
                'disconnected_user': user.split("_")[0],
                'info': "disconnected_user", }))



    async def playerStateChangeSend(self,event):
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

            
    async def addToPlaylistSend(self,event):
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


    async def removeFromPlaylistSend(self, event):
        username = event['username']
        room = rooms[self.room_group_name]
        await self.send(text_data=json.dumps({
                'action': "removeFromPlaylist",
                'playlistupdate': room.playlist,
                'username':username,
            }))


    async def loadVideoSend(self,event):
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

    async def usersCountSend(self,event):
        room = rooms[self.room_group_name]
        await self.send(text_data=json.dumps({
                'room_users': room.room_users,
                'info': "room_users",
            }))

    async def giveTimeSend(self,event):
        room = rooms[self.room_group_name]
        if self.user.username == room.room_users[0]:
            await self.send(text_data=json.dumps({
                'action': "give_time",
            }))

    



