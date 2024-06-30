//agora.io implementation
const APP_ID = "7c57ad2e2f8e4369b316a13082f2c2ea";
const CHANNEL = sessionStorage.getItem("room");
const TOKEN = sessionStorage.getItem("token");
let UID = Number(sessionStorage.getItem("UID"));
const client = AgoraRTC.createClient({ mode: "rtc", codec: "vp8" });
let endbutClicked = false;

let localTracks = [];
let remoteUsers = {};
let role = document.getElementById("role").innerHTML;

let joinAndDisplayLocalStream = async () => {
    client.on('user-published', handleUserJoined);
    client.on('user-left', handleUserLeft)
    try{
        await client.join(APP_ID, CHANNEL, TOKEN, UID);
    } catch (error) {   
        console.error(error);
        window.open("/vidchat", "_self");
    }
    if (role === "student") {
        localTracks = await AgoraRTC.createMicrophoneAndCameraTracks();
        let player = `<div class="video-container" style="border-radius: 20px;height: 250px;width: 300px" id="user-container-${UID}">
        <div class="video-player" style="border-radius: 20px;height: 250px;width: 300px" id="user-${UID}"></div>
        </div>`
        document.getElementById("video-streams").insertAdjacentHTML('beforeend', player);
        localTracks[1].play(`user-${UID}`);
    }
    await client.publish([localTracks[0],localTracks[1]]);
    // await client.leave();
};

let handleUserJoined = async (user, mediaType) => {
        remoteUsers[user.uid] = user;   
        await client.subscribe(user, mediaType);
        if (mediaType === 'video') {
            let player = document.getElementById(`user-container-${user.uid}`)
            if (player!=null){
                player.remove()
            }
                player = `<br><div class="video-container" style="border-radius: 20px;height: 250px;width: 300px" id="user-container-${user.uid}">
                <div class="video-player" style="border-radius: 20px;height: 250px;width: 300px" id="user-${user.uid}"></div>
                </div>`
                document.getElementById("video-streams").insertAdjacentHTML('beforeend', player);
                user.videoTrack.play(`user-${user.uid}`);
            
        }
    }

let handleUserLeft = async (user) => {
    delete remoteUsers[user.uid];
    document.getElementById("video-streams").removeChild(document.getElementById(`user-container-${user.uid}`));
    setTimeout(function() {
        chatSocket.send(JSON.stringify({ message: "End exam(url changed)", username: document.getElementById("me").innerHTML, end: "true"}));
    }, 100);
};

joinAndDisplayLocalStream();

//visibility checking
var examid = document.getElementById('examid').innerHTML;
var submitClicked = false;
var visibilityCheckDelay = 1000;

if (role=="student"){
document.getElementById('submittest').onclick = function() {
    chatSocket.send(JSON.stringify({ message: "End exam", username: document.getElementById("me").innerHTML, end: "submit"}));
    submitClicked = true;
    localStorage.clear();
}}

window.history.pushState(null, "", window.location.href);
window.onpopstate = function() {
    window.history.pushState(null, "", window.location.href);
}

function addVisibilityChangeListener() {
    if (typeof document.hidden !== "undefined") {
        document.addEventListener("visibilitychange", handleVisibilityChange);
    } else if (typeof document.msHidden !== "undefined") {
        document.addEventListener("msvisibilitychange", handleVisibilityChange);
    } else if (typeof document.webkitHidden !== "undefined") {
        document.addEventListener("webkitvisibilitychange", handleVisibilityChange);
    }
}

addVisibilityChangeListener();

function handleVisibilityChange() {
    setTimeout(function() {
        if ((document.hidden || document.msHidden || document.webkitHidden) && !submitClicked) {
            window.location.href = "/vidchat/examterminated/" + examid;
        }
    }, visibilityCheckDelay);
}

//timer implementation
document.addEventListener('DOMContentLoaded', ()=>{
    var examEndTimeStr = document.getElementById('exam_end_time').innerHTML;
    var examEndTime = Math.floor(new Date(examEndTimeStr).getTime() / 1000);
    console.log(examEndTimeStr);

    function parseCustomDateString(dateStr) {
        var dateParts = dateStr.split(', ');
        var date = dateParts[0] + ', ' + dateParts[1]; // "May 25, 2024"
        var timeParts = dateParts[2].split(' ');
        var time = timeParts[0]; // "2:30"
        var meridian = timeParts[1]; // "p.m."

        // Convert time to 24-hour format
        var timeComponents = time.split(':');
        var hours = parseInt(timeComponents[0], 10);
        var minutes = parseInt(timeComponents[1], 10);
        if (meridian === 'p.m.' && hours < 12) {
            hours += 12;
        }
        if (meridian === 'a.m.' && hours === 12) {
            hours = 0;
        }

        var dateISO = new Date(date + ' ' + ('0' + hours).slice(-2) + ':' + ('0' + minutes).slice(-2) + ':00').toISOString();
        return new Date(dateISO);
    }

    var examEndTimeTemp = parseCustomDateString(examEndTimeStr);
    var examEndTime = Math.floor(examEndTimeTemp.getTime() / 1000);
    console.log(examEndTimeTemp)

    function updateTimer() {
        var currentTime = Math.floor(Date.now() / 1000);
        var timeLeft = examEndTime - currentTime;
        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            document.getElementById('timer').innerHTML = 'Time expired!';
            if (role === "student") {
                var form = document.getElementById('exam-form');
                form.submit();
                alert("Time Over! Your exam has been submitted automatically.")
            } else {
                window.location.href = "/";
                alert("Time Over! Exam has been ended automatically.")
            }
        } else {
            var minutes = Math.floor(timeLeft / 60);
            var seconds = timeLeft % 60;
            document.getElementById('timer').innerHTML = minutes + 'min ' + seconds + 'sec';
        }
    }

    updateTimer();
    var timerInterval = setInterval(updateTimer, 1000);

    if (role=="student") checkWebcamAccess();
});

//chat using websocket part
const roomName = JSON.parse(document.getElementById('room-name').textContent);

const chatSocket = new WebSocket(
    'ws://localhost:8000/ws/chat/'+roomName+'/'
);

window.addEventListener('load', function(){
    var scrollablediv = document.getElementById('scrollablediv');
    scrollablediv.scrollTop = scrollablediv.scrollHeight;
});

chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    
    if (data.message.trim() == "Exam has been ended by the proctor." && data.end == "true"){
        window.location.href = "/vidchat/examterminated/" + examid;
    }else if (data.message.trim() == "End exam" && data.end == "submit"){
        localStorage.clear();
        window.location.href = "/";
        alert("Exam submitted by student successfully!");
    }else if (data.message.trim() == "End exam(url changed)" && data.end == "true"){
        window.location.href = "/vidchat/examterminated/" + examid;
    }else{
    let messageContent = `<p>${data.message}</p>`;
    if (data.message.trim() !== "") {
        let liTag = document.createElement("li");
        liTag.innerHTML =
            "<br>" +
            messageContent;

        if (document.getElementById("me").innerHTML === data.username) {
            liTag.style.color = "white";
        } else {
            liTag.style.color = "orange";
        }
        document.querySelector("#chat-log").appendChild(liTag);
    }
    }

    var scrollablediv = document.getElementById("scrollablediv");
    scrollablediv.scrollTop = scrollablediv.scrollHeight;
};

chatSocket.onclose = function (e) {
    console.error("Chat socket closed unexpectedly");
};

document.querySelector("#chat-message-input").focus();
document.querySelector("#chat-message-input").onkeyup = function (e) {
    if (e.key === "Enter") {
        document.querySelector("#chat-message-submit").click();
    }
};

document.querySelector("#chat-message-submit").onclick = function (e) {
    const messageInputDom = document.querySelector("#chat-message-input");
    const message = messageInputDom.value;
    chatSocket.send(JSON.stringify({ message: message, username: document.getElementById("me").innerHTML, end: "false"}));
    messageInputDom.value = "";
};

if (role == "proctor") {
    document.getElementById("end-exam").onclick = function (e) {
        endbutClicked = true;
        const message = "Exam has been ended by the proctor.";
        chatSocket.send(JSON.stringify({ message: message, username: document.getElementById("me").innerHTML, end: "true"}));
    }
}

//making content visible only after webcam access is granted.
function checkWebcamAccess(){
    const questions = document.getElementById('questions-div');
    const mess = document.getElementById('stat-message');

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            questions.classList.remove('hidden');
            mess.textContent = '';
            stream.getTracks().forEach(track => track.stop());
        })
        .catch(error => {
            mess.textContent = "Questions will be visible only after granting webcam access. Please allow access to the webcam to continue.";
            questions.classList.add('hidden');
        });
}





// function updateTimer() {
//     var storedTimerValue = localStorage.getItem(`timerValue_${examid}`);
//     var milliseconds = parseInt(storedTimerValue);
    
//     var minutes = Math.floor(milliseconds / (1000 * 60));
//     var seconds = Math.floor((milliseconds % (1000 * 60)) / 1000);
    
//     document.getElementById('timer').innerHTML = minutes + 'm ' + seconds + 's';
    
//     if (milliseconds <= 0) {
//         clearInterval(timerInterval);
//         document.getElementById('timer').innerHTML = 'Time expired!';
//         if (role=="student"){
//         var form = document.getElementById('exam-form');
//         form.submit();
//         }else{
//             window.location.href="/";
//         }
//         localStorage.clear();
//     } else {
//         milliseconds -= 1000;
//         localStorage.setItem(`timerValue_${examid}`, milliseconds); 
//     }
// }

// var storedTimerValue = localStorage.getItem(`timerValue_${examid}`);
// var milliseconds;
// if (storedTimerValue) {
//     milliseconds = parseInt(storedTimerValue);
// } else {
//     var durationFromDjango = parseInt(document.getElementById('duration').innerHTML);
//     milliseconds = durationFromDjango * 60 * 1000; 
//     localStorage.setItem(`timerValue_${examid}`, milliseconds); 
// }
// var timerInterval = setInterval(updateTimer, 1000);



//Fulscreen implementation trial

// document.addEventListener('DOMContentLoaded', function() {
//     document.getElementById('whole').style.display = 'none';
//     document.getElementById('fsb').style.display = 'block';
// });

// function gofullscreen(){
//     var elem = document.documentElement;
//     if (elem.requestFullscreen) {
//         elem.requestFullscreen();
//     } else if (elem.mozRequestFullScreen) { 
//         elem.mozRequestFullScreen();
//     } else if (elem.webkitRequestFullscreen) { 
//         elem.webkitRequestFullscreen();
//     } else if (elem.msRequestFullscreen) { 
//         elem.msRequestFullscreen();
//     }
//     document.getElementById('whole').style.display = 'block';
//     document.getElementById('fsb').style.display = 'none';
// }