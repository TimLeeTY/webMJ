function setInitial(){
    for (var t=0; t<14; t++){
        (function(){
            var tile;
            var i = t
            tile=document.getElementById('hand-0-'+i);
            tile.addEventListener('click', function(){
                chooseDiscard(i-1);
            });
        })();
    };
    for (var c=0; c<5; c++){
        (function(){
            var i = c
            var btn = document.getElementById('button'+i)
            btn.addEventListener('click', function(){
                socket.emit('optChoice', roomID, i+1)
                hideChoices() 
            });
            var winBtn = document.getElementById('WinButton'+i)
            winBtn.addEventListener('click', function(){
                socket.emit('winChoice', roomID, i+1)
                hideWin() });
        })();
    };
    var ignorebtn=document.getElementById('ignorebutton');
    ignorebtn.addEventListener('click', function(){
        socket.emit('optChoice', roomID, 0);
        hideChoices() });
    var ignoreWinbtn=document.getElementById('ignoreWinButton');
    ignoreWinbtn.addEventListener('click', function(){
        socket.emit('winChoice', roomID, 0);
        hideWin() });
    var hideWinbtn=document.getElementById('hideWinButton');
    hideWinbtn.addEventListener('click', function(){
        socket.emit('connected_to_game', roomID);
        hideWin() });
    var leaveButton = document.getElementById('leaveRoom');
    var leaveLink = leaveButton.href
    leaveButton.removeAttribute('href')
    leaveButton.style.cursor = 'pointer'
    leaveRoom.addEventListener('click', function(){
        if (window.confirm('The game will end if you leave, are you sure?')){
            window.location.replace(leaveLink)
        }
    });
}

function writeNames(players, wind, dealer, whoseTurn){
    for (var i=0; i < 4; i++){
        var username = '<b>'+players[i]+'</b>'+'\n'+wind[i];
        if (players[i] == whoseTurn){
            document.getElementById('tri-left-'+i).style.display = 'inline-block';
            document.getElementById('tri-right-'+i).style.display = 'inline-block';
        }
        var c = i
        var nameplate = document.getElementById('usernameText'+c)
        nameplate.innerHTML = username
    }
}

function drawHands(handSizes){
    for (var hand=0; hand <3; hand++){
        var t;
        var tile;
        for (t=0; t<handSizes[hand]; t++){
            tile=document.getElementById('hand-'+(hand+1)+'-'+(t+1)%14);
            tile.style.backgroundImage = "url('/media/b-0-.svg')";
        }
        for (t=handSizes[hand]+1; t<14; t++){
            tile=document.getElementById('hand-'+(hand+1)+'-'+t);
            tile.style.backgroundImage = "none";
        }
    }
}

function drawDiscards(tiles, player){
    if (tiles.length == 0){
        for (var t=0; t<22; t++){
            var tile;
            tile=document.getElementById('discard-'+player+'-'+t);
            tile.style.backgroundImage = "none"
        }
    }
    else{
        for (var t=0; t<tiles.length; t++){
            var tile;
            var s=tiles[t][0];
            var v=tiles[t][1] + 1;
            tile=document.getElementById('discard-'+player+'-'+t);
            tile.style.backgroundImage = "url('/media/"+s+"-"+v+"-.svg')"
        }
    }
}

function drawSets(tiles, player){
    if (tiles.length == 0){
        for (var t=0; t<16; t++){
            var tile;
            tile=document.getElementById('set-'+player+'-'+t);
            tile.style.backgroundImage = "none"
        }
    }
    else{
        for (t=0; t<tiles.length; t++){
            var tile;
            var s=tiles[t][0];
            var v=tiles[t][1] + 1;
            tile=document.getElementById('set-'+player+'-'+t);
            tile.style.backgroundImage = "url('/media/"+s+"-"+v+"-.svg')"
        }
    }
}

function showPlayerHand(tiles){
    var tl = tiles.length
    for (var t=0; (t<tl); t++){
        var s=tiles[t][0];
        var v=tiles[t][1] + 1;
        var tile=document.getElementById('hand-0-'+(t+1)%14);
        tile.style.backgroundImage = "url('/media/"+s+"-"+v+"-.svg')"
    }
    for (var t=tl; t<=13; t++){
        document.getElementById('hand-0-'+(t+1)%14).style.backgroundImage = "none"
    }
}
function playerDraw(newTile){
    var tile;
    tile=document.getElementById('hand-0-0');
    tile.style.backgroundImage = "url('/media/"+newTile[0]+"-"+(newTile[1]+1)+"-.svg')"
}

function draw(player){
    var tile;
    tile=document.getElementById('hand-'+player+'-0');
    tile.style.backgroundImage = "url('/media/b-0-.svg')";
}

function discardTileDisp(newTile, player, loc){
    var discTile
    discTile=document.getElementById('discard-'+player+'-'+loc);
    discTile.style.backgroundImage = "url('/media/"+newTile[0]+"-"+(newTile[1]+1)+"-.svg')";
}

function discardTileHand(player){
    var tile;
    tile=document.getElementById('hand-'+player+'-0');
    tile.style.backgroundImage = "none";
}

function addSet(player, loc, newSet){
    for (var i=0; i<newSet.length; i++){
        var setTile
        setTile=document.getElementById('set-'+player+'-'+(loc+i));
        setTile.style.backgroundImage = "url('/media/"+newSet[i][0]+"-"+(newSet[i][1]+1)+"-.svg')";
    }
}

function whoseTurn(player){
    for (var i=0; i<4; i++){
        var leftTri = document.getElementById('tri-left-'+i);
        var rightTri = document.getElementById('tri-right-'+i);
        if (i == player) {
            leftTri.style.display = 'inline-block'
            rightTri.style.display = 'inline-block'
        }
        else{
            leftTri.style.display = 'none'
            rightTri.style.display = 'none'
        }
    }
}

function showSet(newSet, player, loc){
    var i;
    for (i=0; i<newSet.length; i++){
        var tile;
        tile=document.getElementById('set-'+player+'-'+(loc+i));
        tile.style.backgroundImage = "url('/media/"+newSet[i][0]+"-"+(newSet[i][1]+1)+"-.svg')"
    }
}

function oneHand(player, size){
    var i;
    for (i=13; i>size; i--){
        var tile;
        tile=document.getElementById('hand-'+player+'-'+i);
        tile.style.backgroundImage = "none";
    }
}

function chooseDiscard(tile){
    socket.emit('discardTile', tile, roomID)
    // emit choice to server
}

function showChoices(tile, types, sets){
    var center = document.getElementById('center');
    for (var i=0; i<sets.length; i++){
        (function(){
            var choice = document.getElementById('choice'+i);
            choice.style.display = 'inline-block'
            var newTile = document.getElementById('choice'+i+'-0');
            newTile.style.backgroundImage = "url('/media/"+tile[0]+"-"+(tile[1]+1)+"-.svg";
            for (var j=0; j<sets[i].length; j++){
                (function(){
                    var setTile
                    setTile = document.getElementById('choice'+i+'-'+(j+1));
                    setTile.style.backgroundImage = "url('/media/"+sets[i][j][0]+"-"+(sets[i][j][1]+1)+"-.svg";
                })()}
        var btn = document.getElementById('button'+i);
        btn.innerHTML = types[i];
        })() }
    var choice5 = document.getElementById('choice5');
    choice5.style.display = 'inline-block'
    center.style.display= "inline-block";
}

function showWin(tile, hand){
    var center = document.getElementById('centerWin');
    var winButton = document.getElementById('WinButton0');
    winButton.style.visibility = 'visible';
    var choice = document.getElementById('win0');
    choice.style.display = 'inline-block'
    var newTile = document.getElementById('win0-0');
    newTile.style.backgroundImage = "url('/media/"+tile[0]+"-"+(tile[1]+1)+"-.svg";
    for (var j=0; j<hand.length; j++){
        (function(){
            var setTile
            setTile = document.getElementById('win0-'+(j+1));
            setTile.style.backgroundImage = "url('/media/"+hand[j][0]+"-"+(hand[j][1]+1)+"-.svg";
            })()}
    var choice5 = document.getElementById('win5');
    var cancelBtn = document.getElementById('ignoreWinButton');
    cancelBtn.style.display = 'inline-block';
    var title = document.getElementById('playerWinText');
    title.innerHTML = '';
    choice5.style.display = 'inline-block';
    center.style.display= "inline-block";
}

function playerWin(player, tile, hand){
    var center = document.getElementById('centerWin');
    var choice = document.getElementById('win0');
    choice.style.display = 'inline-block'
    var newTile = document.getElementById('win0-0');
    newTile.style.backgroundImage = "url('/media/"+tile[0]+"-"+(tile[1]+1)+"-.svg";
    for (var j=0; j<hand.length; j++){
        (function(){
            var setTile
            setTile = document.getElementById('win0-'+(j+1));
            setTile.style.backgroundImage = "url('/media/"+hand[j][0]+"-"+(hand[j][1]+1)+"-.svg";
        })()};
    var choice5 = document.getElementById('win5');
    choice5.style.display = 'inline-block';
    var hideBtn = document.getElementById('hideWinButton');
    hideBtn.style.display = 'inline-block';
    var title = document.getElementById('playerWinText');
    title.textContent = player+' wins!';
    center.style.display= "inline-block";
}

function hideChoices(){
    var center = document.getElementById('center');
    center.style.display= "none";
    for (var i=0; i<5; i++){
        (function(){
            var choice = document.getElementById('choice'+i);
            choice.style.display = 'none';
            for (var j=0; j<4; j++){
                (function(){
                    var setTile;
                    setTile = document.getElementById('choice'+i+'-'+j);
                    setTile.style.backgroundImage = "none";
                })()}
        })() }
    var choice5 = document.getElementById('choice5');
    choice5.style.display = 'none';
}

function hideWin(){
    var center = document.getElementById('centerWin');
    center.style.display= "none";
    for (var i=0; i<5; i++){
        (function(){
            var winButton = document.getElementById('WinButton'+i);
            winButton.style.visibility= 'hidden';
            var choice = document.getElementById('win'+i);
            choice.style.display = 'none';
            for (var j=0; j<4; j++){
                (function(){
                    var setTile;
                    setTile = document.getElementById('win'+i+'-'+j);
                    setTile.style.backgroundImage = "none";
                })()}
        })() }
    var title = document.getElementById('playerWinText');
    title.textContent = '';
    var choice5 = document.getElementById('win5');
    choice5.style.display = 'none';
    var cancelBtn = document.getElementById('ignoreWinButton');
    cancelBtn.style.display = 'none';
    var hideBtn = document.getElementById('hideWinButton');
    hideBtn.style.display = 'none';
}

var socket = io();
var playerList = [0, 0, 0, 0];
var wind = ['east', 'south', 'west', 'north']
var windList = [0, 0, 0, 0] 

socket.on('initialise', function(players, pos, whoseTurn){
    dealer = players[0]
    for (i=0; i<4; i++){
        playerList[i] = players[(i+pos)%4];
        windList[i] = wind[(i+pos)%4];
    }
    writeNames(playerList, windList, dealer, whoseTurn)
});

socket.on('showHand', function(tiles){
    showPlayerHand(tiles);
});

socket.on('drawHands', function(handSizes){
    drawHands(handSizes);
});

socket.on('oneHand', function(player, handSize){
    player = playerList.indexOf(player);
    if (player !== 0){
        oneHand(player, handSize)
    }
});

socket.on('discardTileDisp', function(newTile, player, loc){
    player = playerList.indexOf(player);
    discardTileDisp(newTile, player, loc);
});

socket.on('discardTileHand', function(player){
    player = playerList.indexOf(player);
    discardTileHand(player);
});

socket.on('addSet', function(player, loc, newSet){
    player = playerList.indexOf(player);
    addSet(player, loc, newSet);
    whoseTurn(player);
});

socket.on('drawDiscards', function(discDict){
    for (var i=0; i<4; i++){
        drawDiscards(discDict[playerList[i]], i);
    }
});

socket.on('drawSets', function(setDict){
    for (var i=0; i<4; i++){
        drawSets(setDict[playerList[i]], i);
    }
});

socket.on('drawPlayerSet', function(player, sets){
    player = playerList.indexOf(player);
    drawSets(sets, player);;
});

socket.on('playerDraw', function(tile){
    console.log(playerList[0]+'has drawn')
    playerDraw(tile)
});

socket.on('blindDraw', function(player){
    player = playerList.indexOf(player);
    whoseTurn(player);
    if (player !== 0){
        draw(player)
    }
});

socket.on('joinRoom', function(players, roomID){
    socket.emit('joinIORoom', roomID)
});

socket.on('leaveRoom', function(roomID){
    socket.emit('leaveIORoom', roomID)
});

socket.on('showChoices', function(tile, types, sets){
    showChoices(tile, types, sets)
});

socket.on('showWin', function(tile, hand){
    showWin(tile, hand)
});

socket.on('playerWin', function(player, tile, hand){
    hideWin()
    playerWin(player, tile, hand)
});

window.onload = function(){
    socket.emit('connected_to_game', roomID);
    setInitial();
}
