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
        self.index = 0

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
        print("the index is + " + index)
        for i in range(len(self.playlist)):
            if self.playlist[i]['video_id']  == videoID.split("*")[1] and str(self.playlist[i]['index']) == index:

                del self.playlist[i]
                print(self.playlist)
                    
                break
                
            
    def room_info(self):
        room_info = {"id":self.room_id,"host":self.host,"room_users":self.room_users}
        return room_info