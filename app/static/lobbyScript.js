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

