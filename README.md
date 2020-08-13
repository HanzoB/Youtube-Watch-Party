# Youtube-Watch-Party [SyncPin]

A youtube video syncing app built on python and django framework.
<br><br>
![syncpindisplay](https://user-images.githubusercontent.com/13599606/90090608-5c903980-dd1c-11ea-8cf1-0fa25291e339.jpg)

## Dependencies

[Redis](https://github.com/redis/redis)

```bash
sudo apt-get install python3
```
<br>

```bash
pip install Django==3.0.7
```
<br>

```bash
pip install channels-redis
```


## Running the server 
```bash
manage.py runserver 0.0.0.0:8000
```


## Description
This django app utilizes websockets for syncing user inputted youtube videos. It allows interaction between all users who enter a room with a common room-id. This app functions on youtube's native controllers by tracking every user's video state ( pause/play/ current time), once a state change event is triggered, it is emitted to all users within the room so that the video state can be replicated.

<b>Features:<b>
  <li>Chat</li>
  <li>Playlist</li>
  <li>Username assignment</li>
  <li>Universal room control</li>
  

<br>

<b>[Live demo](https://syncpin.net)<b>
