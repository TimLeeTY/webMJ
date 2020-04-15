function playerReady(playerOrder, readyBool){
    var readyID = document.getElementById('ready-'+playerOrder)
    if (readyBool) {
    readyID.innerHTML = '&#10004'
    }
    else {
    readyID.innerHTML = ''
    }
}

function ready(){
    socket.emit('lobby_ready', roomID, true);
    var readyBtn = document.getElementById('readyGame')  
    readyBtn.removeEventListener('click', ready);
    readyBtn.innerHTML = 'unready'
    readyBtn.addEventListener('click', unready);
}

function unready(){
    socket.emit('lobby_ready', roomID, false);
    var readyBtn = document.getElementById('readyGame')  
    readyBtn.removeEventListener('click', unready);
    readyBtn.innerHTML = 'ready'
    readyBtn.addEventListener('click', ready);
}

var readyBtn = document.getElementById('readyGame')  
if (document.body.contains(readyBtn)){
    if (readyBtn.innerHTML == 'ready'){
        readyBtn.addEventListener('click', ready);
    }
    if (readyBtn.innerHTML == 'unready'){
        readyBtn.addEventListener('click', unready);
    }
}

var socket = io();

socket.emit('connected_to_lobby', roomID);

socket.on('playerChange', function(){
    console.log('player change')
    location.reload();
});

socket.on('leaveRoom', function(){
    socket.emit('leave', roomID);
    location.reload();
});

socket.on('playerReady', function(playerOrder, readyBool){
    playerReady(playerOrder, readyBool)
});

var tileDict = [[0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7], [0, 8], [0, 9], [1, 1], [1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [1, 7], [1, 8], [1, 9], [2, 1], [2, 2], [2, 3], [2, 4], [2, 5], [2, 6], [2, 7], [2, 8], [2, 9], [3, 1], [3, 2], [3, 3], [3, 4], [4, 1], [4, 2], [4, 3]]
window.onload = function(){
    for (var i=0; i<tileDict.length; i++){
        // Cache tile images
        var t = tileDict[i];
        var preload = new Image();
        preload.scr = "url('https://webmj-assets.s3.us-east-2.amazonaws.com/"+t[0]+"-"+t[1]+"-.svg";
    }
}
