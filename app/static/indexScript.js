var joinBtn = document.getElementById('joinBtn')

joinBtn.addEventListener('click', function(){
    var joinInput = document.getElementById('roomName')
    var roomName = joinInput.value;
    console.log(roomName)
    if (roomName !== ''){
        var link = '/room/'+roomName+'/join';
        window.location.href = link;
    };
});

var input = document.getElementById('roomName')
input.addEventListener("keyup", function(event) {
  if (event.keyCode === 13) {
    event.preventDefault();
    joinBtn.click();
  }
});

