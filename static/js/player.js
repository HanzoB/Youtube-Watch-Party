// 2. This code loads the IFrame Player API code asynchronously.
var tag = document.createElement('script');

tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

// 3. This function creates an <iframe> (and YouTube player)
//    after the API code downloads.
var player;
let seektime = "";
var load_id = "";
var IsPlaying;
var userName = "";
var confirmation;
let expectedRunTime = 0.0;
let videoLastStartTime = 0.0;
let chatSocket = {};
var isSeeking = false;



function onYouTubeIframeAPIReady() {
    player = new YT.Player('player', {
        height: '390',
        width: '640',
        playerVars: {
            'autoplay': 0,
            'controls': 1,
            'rel:': 0
        },
        events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange
        }
    });


}

var playerReady = false;
// 4. The API will call this function when the video player is ready.
function onPlayerReady(event) {
    playerReady = true;
    if (load_id != "") {
        player.loadVideoById(load_id)
    }
    if (seektime != "") {
        player.seekTo(seektime, true)
    }




    function CheckIfSeeked() {
        //console.log("Actual player time: " + player.getCurrentTime())
        //console.log("Calculated player time: " + (expectedRunTime))
        if (IsPlaying === true) {
            expectedRunTime += 0.5

        }
        console.log("Expected run time: " + expectedRunTime)
        console.log("Actual player time:: " + player.getCurrentTime())

        if (isSeeking === false) {
            if (Math.abs(player.getCurrentTime() - (expectedRunTime)) > 5) {
                chatSocket.send(JSON.stringify({
                    'action': "seek",
                    'data': player.getCurrentTime(),
                }));
                expectedRunTime = player.getCurrentTime()

            }


        } else {
            console.log("Currently Seeking")
        }



    }
    setInterval(CheckIfSeeked, 500)






}


// 5. The API calls this function when the player's state changes.
//    The function indicates that when playing a video (state=1),
//    the player should play for six seconds and then stop.
function onPlayerStateChange(event) {
    if (event.data == YT.PlayerState.ENDED) {

    }
    if (event.data == YT.PlayerState.PLAYING) {
        IsPlaying = true
            //confirmation  += 1
        chatSocket.send(JSON.stringify({
            'action': "play",
            // 'confirmation': confirmation ,
        }));
        date = new Date()
        time = date.getTime() / 1000
        videoLastStartTime = time





    }
    if (event.data == YT.PlayerState.PAUSED) {
        IsPlaying = false
        chatSocket.send(JSON.stringify({
            'action': "pause",
            'confirmation': confirmation,
        }));
        end = new Date()
        expectedRunTime += (end.getTime() / 1000) - videoLastStartTime
        videoLastStartTime = end.getTime() / 1000

        //console.log(expectedRunTime)




    }




}


function YouTubeGetID(url) {
    var ID = '';
    url = url.toString().replace(/(>|<)/gi, '').split(/(vi\/|v=|\/v\/|youtu\.be\/|\/embed\/)/);
    if (url[2] !== undefined) {
        ID = url[2].split(/[^0-9a-z_\-]/i);
        ID = ID[0];
    } else {
        ID = url;
    }
    return ID;
}
$("#loadvideo").on("click", function() {
    url = $("#searchbox").val().match(/(\?|&)v=([^&#]+)/)
    video_id = YouTubeGetID(url)
    document.querySelector('#searchbox').value = ""
    player.loadVideoById(video_id, 0, "default");
    player.stopVideo()
    chatSocket.send(JSON.stringify({
        'action': "load_video",
        'data': video_id
    }));
    setTimeout(function() {
        player.seekTo(0, true)
    }, 100)
});
$("#AddToPlaylist").on("click", function() {
    url = $("#searchbox").val().match(/(\?|&)v=([^&#]+)/)
    video_id = YouTubeGetID(url)
    document.querySelector('#searchbox').value = ""
    chatSocket.send(JSON.stringify({
        'action': "addToPlaylist",
        'data': video_id
    }));
});




$(document).ready(function() {
    $('#exampleModal').modal('show');

});

$("#inviteToRoom").on("click", function() {

    var UrlHolder = document.createElement("input")
    roomURL = window.location.host + "/room/" + room_name

    document.body.appendChild(urlHolder);
    urlHolder.value = roomURL;
    urlHolder.select();
    document.execCommand('copy');
    document.body.removeChild(urlHolder);



})



$("#joinRoom").on("click", function() {
    console.log("before: " + userName)
    userName = $("#username").val()
    console.log("after: " + userName)
    if (userName != "") {
        $('#exampleModal').modal('hide');
        alert("called")
        chatSocket = new WebSocket(
            'ws://' +
            window.location.host +
            '/ws/room/' +
            room_name



        );
        chatSocket.onmessage = WebsocketOnMessage


        chatSocket.onopen = function(e) {
            chatSocket.send(JSON.stringify({
                'username': userName
            }));
        };
        console.log(chatSocket)
    }
    //document.querySelector('#searchbox').value = ""


});





WebsocketOnMessage = function(e) {
    const data = JSON.parse(e.data);
    if (playerReady) {
        if (data.seekTo) {
            if (data.playerstate === "play") {
                setTimeout(function() {
                    player.seekTo(data.seekTo - 0.5, true)
                    player.playVideo()
                }, 500);



            } else if (data.playerstate === "pause") {
                setTimeout(function() {
                    player.seekTo(data.seekTo - 0.5, true)
                    player.pauseVideo()
                    IsPlaying = false
                }, 500);



            }
            console.log("seeking, player ready")
        }
    } else {
        if (data.seekTo) {
            seektime = data.seekTo
        }

    }
    if (data.message) {
        document.querySelector('#chat-log').innerHTML +=
            '<li id="chat-msg">' +
            '<li style="font-family: italic; font-size: 13px; list-style-type: none;">' + data.username + ': </li>' +
            data.message +
            '</li>'


        updateScroll()
    }
    if (data.new_user) {
        document.querySelector('#chat-log').innerHTML +=
            '<li style="font-family: italic; font-size: 13px; list-style-type: none;">' + data.new_user + ' joined the room.' + '</li>'

        updateScroll()

    }
    if (data.action === 'pause') {

        if (IsPlaying === true) {

            player.pauseVideo()
        }

    };
    if (data.action === 'load_video') {
        player.loadVideoById(data.data, 1, "default")
        console.log("called load video")
        setTimeout(function() {
            player.seekTo(0, true)
        }, 500)
    };
    if (data.current_video) {
        if (playerReady) {
            console.log("video is set")
            player.loadVideoById(data.current_video, 1, "default")
            player.playVideo()
        } else {
            load_id = data.current_video

        }
    };
    if (data.action === 'play') {

        if (IsPlaying === false) {

            player.playVideo()
        }
    }
    if (data.action === 'seek') {
        if (data.current_time) {
            console.log("called" + data.current_time)
            console.log(data.current_time)
            date = new Date()
            time = date.getTime() / 1000
            videoLastStartTime = time
            isSeeking = true
            player.seekTo(data.current_time, true)
            expectedRunTime = data.current_time

            function waitseek() {
                if (data.current_time == player.getCurrentTime()) {
                    isSeeking = false
                    console.log("finished seeking")
                    clearInterval(CheckingSeek)
                }

            }

            CheckingSeek = setInterval(waitseek, 100)

        } else {

        }
    };
    if (data.action === "give_time") {
        console.log("give_time")
        chatSocket.send(JSON.stringify({
            'new_user_time': player.getCurrentTime()
        }));

    } else {

    }
    if (data.action === "addToPlaylist") {
        $('#vid-list').append(
            '<div  class="vid-item">' +
            '<div id=' + data.video_id + ' type="button" class="thumb">' +
            '<img src="http://img.youtube.com/vi/' + data.video[0] + '/0.jpg">' +
            '</div>' +
            '<div class="desc">' +
            data.video[1] +
            '</div>' +
            '</div>');



    } else {

    }


};




chatSocket.onclose = function(e) {
    console.log("WebSocket is closed now.");
};



chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function(e) {
    if (e.keyCode === 13) { // enter, return
        const messageInputDom = document.querySelector('#chat-message-input');
        const message = messageInputDom.value;
        chatSocket.send(JSON.stringify({
            'message': message
        }));
        messageInputDom.value = '';
    }
};


function updateScroll() {
    var element = document.getElementById("chat-log");
    element.scrollTop = element.scrollHeight;
};

document.querySelector('.thumb').click(function() {
    alert("called")
    alert(this.id); // or alert($(this).attr('id'));
});

//playlist shiz
$(document).ready(function() {
    $(".arrow-right").bind("click", function(event) {
        event.preventDefault();
        $(".vid-list-container").stop().animate({
            scrollLeft: "+=148"
        }, 750);
    });
    $(".arrow-left").bind("click", function(event) {
        event.preventDefault();
        $(".vid-list-container").stop().animate({
            scrollLeft: "-=148"
        }, 750);
    });
});