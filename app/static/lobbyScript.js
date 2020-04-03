function playerReady(playerOrder, readyBool){
    var readyID = document.getElementById('ready-'+playerOrder)
    if (readyBool) {
    readyID.innerHTML = '&#10004'
    }
    else {
    readyID.innerHTML = ''
    }
}

function playerUnready(playerOrder){
    var readyID = document.getElementById('ready-'+playerOrder)
    readyID.innerHTML = ''
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

