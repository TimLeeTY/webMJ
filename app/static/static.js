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
    var btn = document.getElementById('button0')
    btn.addEventListener('click', function(){
        socket.emit('optChoice', roomID, 1)
        hideChoices() });
    var winBtn = document.getElementById('WinButton0')
    winBtn.addEventListener('click', function(){
        socket.emit('winChoice', roomID, 1)
        hideWin() });
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
        hideWin()
        socket.emit('connected_to_game', roomID); });
    var leaveButton = document.getElementById('leaveRoom');
    var leaveLink = leaveButton.href
    leaveButton.removeAttribute('href')
    leaveButton.style.cursor = 'pointer'
    leaveRoom.addEventListener('click', function(){
        if (window.confirm('The game will end if you leave, are you sure?')){
            window.location.replace(leaveLink)
        }
    });
    for (var i=0; i<tileDict.length; i++){
        // Cache tile images
        var t = tileDict[i];
        var preload = new Image();
        preload.scr = "url('https://webmj-assets.s3.us-east-2.amazonaws.com/"+t[0]+"-"+t[1]+"-.svg";
    }
}

function writeNames(players, wind, dealer, whoseTurn){
    for (var i=0; i < 4; i++){
        var username = '<b>'+players[i].replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/&/g, '&amp;')+'</b>'+'\n'+wind[i];
        if (i == whoseTurn){
            document.getElementById('tri-left-'+i).style.display = 'inline-block';
            document.getElementById('tri-right-'+i).style.display = 'inline-block';
        }
        else {
            document.getElementById('tri-left-'+i).style.display = 'none';
            document.getElementById('tri-right-'+i).style.display = 'none';
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
            tile.style.backgroundImage = "url('https://webmj-assets.s3.us-east-2.amazonaws.com/b-0-.svg')";
            tile.style.visibility = "visible"
        }
        for (t=handSizes[hand]+1; t<14; t++){
            tile=document.getElementById('hand-'+(hand+1)+'-'+t);
            tile.style.backgroundImage = "none";
            tile.style.visibility = "hidden"
        }
    }
}

function drawDiscards(tiles, player){
    if (tiles.length == 0){
        for (var t=0; t<22; t++){
            var tile;
            tile=document.getElementById('discard-'+player+'-'+t);
            tile.style.backgroundImage = "none"
            tile.style.visibility = "hidden"
        }
    }
    else{
        for (var t=0; t<tiles.length; t++){
            var tile=document.getElementById('discard-'+player+'-'+t);
            drawTile(tile, tiles[t])
        }
    }
}

function drawSets(tiles, player){
    if (tiles.length == 0){
        for (var t=0; t<16; t++){
            var tile;
            tile=document.getElementById('set-'+player+'-'+t);
            tile.style.backgroundImage = "none"
            tile.style.visibility = "hidden"
        }
    }
    else{
        for (t=0; t<tiles.length; t++){
            var tile=document.getElementById('set-'+player+'-'+t);
            drawTile(tile, tiles[t])
        }
    }
}

function showPlayerHand(tiles){
    var tl = tiles.length
    for (var t=0; (t<tl); t++){(function(){
        var tile=document.getElementById('hand-0-'+(t+1)%14);
        drawTile(tile, tiles[t])
    })() }
    for (var t=tl; t<=13; t++){
        document.getElementById('hand-0-'+(t+1)%14).style.backgroundImage = "none"
        document.getElementById('hand-0-'+(t+1)%14).style.visibility = "hidden"
    }
}
function playerDraw(newTile){
    var tile=document.getElementById('hand-0-0');
    drawTile(tile, newTile)
}

function draw(player){
    var tile;
    tile=document.getElementById('hand-'+player+'-0');
    tile.style.backgroundImage = "url('https://webmj-assets.s3.us-east-2.amazonaws.com/b-0-.svg')";
    tile.style.visibility = "visible"
}

function discardTileDisp(newTile, player, loc){
    var discTile
    discTile=document.getElementById('discard-'+player+'-'+loc);
    drawTile(discTile, newTile)
}

function discardTileHand(player){
    var tile;
    tile=document.getElementById('hand-'+player+'-0');
    tile.style.backgroundImage = "none";
    tile.style.visibility = "hidden"
}

function addSet(player, loc, newSet){
    for (var i=0; i<newSet.length; i++){
        var setTile = document.getElementById('set-'+player+'-'+(loc+i));
        drawTile(setTile, newSet[i])
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

function oneHand(player, size){
    var i;
    for (i=13; i>=size; i--){
        var tile;
        tile=document.getElementById('hand-'+player+'-'+i);
        tile.style.backgroundImage = "none";
        tile.style.visibility = "hidden"
    }
    tile=document.getElementById('hand-'+player+'-0');
    tile.style.backgroundImage = "url('https://webmj-assets.s3.us-east-2.amazonaws.com/b-0-.svg')";
    tile.style.visibility = "visible"
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
            drawTile(newTile, tile)
            for (var j=0; j<sets[i].length; j++){
                (function(){
                    var setTile = document.getElementById('choice'+i+'-'+(j+1));
                    drawTile(setTile, sets[i][j])
                })()}
        var btn = document.getElementById('button'+i);
        btn.textContent = types[i];
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
    drawTile(newTile, tile)
    for (var j=0; j<hand.length; j++){
        (function(){
            var setTile = document.getElementById('win0-'+(j+1));
            drawTile(setTile, hand[j])
            })()}
    var choice5 = document.getElementById('win5');
    var cancelBtn = document.getElementById('ignoreWinButton');
    cancelBtn.style.display = 'inline-block';
    var title = document.getElementById('playerWinText');
    title.innerHTML = '';
    choice5.style.display = 'inline-block';
    center.style.display= "inline-block";
}

function playerWin(player, tile, hand, pointDict){
    var center = document.getElementById('centerWin');
    var choice = document.getElementById('win0');
    choice.style.display = 'inline-block'
    var newTile = document.getElementById('win0-0');
    drawTile(newTile, tile)
    for (var j=0; j<hand.length; j++){
        (function(){
            var setTile
            setTile = document.getElementById('win0-'+(j+1));
            drawTile(setTile, hand[j])
        })()};
    var choice5 = document.getElementById('win5');
    choice5.style.display = 'inline-block';
    var hideBtn = document.getElementById('hideWinButton');
    hideBtn.style.display = 'inline-block';
    var title = document.getElementById('playerWinText');
    title.textContent = player+' wins!';
    center.style.display= "inline-block";
}

function gameDraw(){
    var center = document.getElementById('centerWin');
    var choice5 = document.getElementById('win5');
    choice5.style.display = 'inline-block';
    var hideBtn = document.getElementById('hideWinButton');
    hideBtn.style.display = 'inline-block';
    var title = document.getElementById('playerWinText');
    title.textContent = 'game ends in draw!';
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
                    undrawTile(setTile);
                })()}
        })() }
    var choice5 = document.getElementById('choice5');
    choice5.style.display = 'none';
}

function hideWin(){
    var center = document.getElementById('centerWin');
    center.style.display= "none";
    var winButton = document.getElementById('WinButton0');
    winButton.style.visibility= 'hidden';
    var choice = document.getElementById('win0');
    choice.style.display = 'none';
    for (var j=0; j<4; j++){
        (function(){
            var setTile;
            setTile = document.getElementById('win0-'+j);
            undrawTile(setTile);
        })()}
    var title = document.getElementById('playerWinText');
    title.textContent = '';
    var choice5 = document.getElementById('win5');
    choice5.style.display = 'none';
    var cancelBtn = document.getElementById('ignoreWinButton');
    cancelBtn.style.display = 'none';
    var hideBtn = document.getElementById('hideWinButton');
    hideBtn.style.display = 'none';
}

function drawTile(tileEle, tileInd){
    var tileVal = tileDict[tileInd];
    var label = tileEle.childNodes[1];
    tileEle.style.backgroundImage = "url('https://webmj-assets.s3.us-east-2.amazonaws.com/"+tileVal[0]+"-"+tileVal[1]+"-.svg";;
    tileEle.style.visibility = "visible";
    if (tileVal[0] < 3){
        label.textContent = tileVal[1] + ' ' + suitLabel[tileVal[0]];
    }
    else {
        label.textContent = honorLabel[tileVal[0]-3][tileVal[1]-1];
    };
}

function undrawTile(tileEle){
    tileEle.style.backgroundImage = "none";
    tileEle.style.visibility = "hidden";
}

var socket = io();
var playerOrder
var tileDict = [[0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7], [0, 8], [0, 9], [1, 1], [1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [1, 7], [1, 8], [1, 9], [2, 1], [2, 2], [2, 3], [2, 4], [2, 5], [2, 6], [2, 7], [2, 8], [2, 9], [3, 1], [3, 2], [3, 3], [3, 4], [4, 1], [4, 2], [4, 3]]
var suitLabel = ['Dots', 'Bamboo', 'Numbers']
var honorLabel = [['East', 'South', 'West', 'North'], ['Red', 'Green', 'White']]

socket.on('initialise', function(players, pos, whoseTurn, order){
    var wind = ['east', 'south', 'west', 'north'];
    var windList = ['', '', '', ''];
    var playerList = ['', '', '', ''];
    dealer = players[0]
    playerOrder = order
    whoseTurn = (whoseTurn - order + 4) %4
    for (i=0; i<4; i++){
        playerList[i] = players[(i+order+ 4)%4];
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
    player = (player - playerOrder + 4) % 4 ;
    if (player !== 0){
        oneHand(player, handSize)
    }
});

socket.on('discardTileDisp', function(newTile, player, loc){
    player = (player - playerOrder + 4) % 4 ;
    discardTileDisp(newTile, player, loc);
});

socket.on('discardTileHand', function(player){
    player = (player - playerOrder + 4) % 4 ;
    discardTileHand(player);
});

socket.on('addSet', function(player, loc, newSet){
    player = (player - playerOrder + 4) % 4 ;
    addSet(player, loc, newSet);
    whoseTurn(player);
});

socket.on('drawDiscards', function(discDict){
    for (var i=0; i<4; i++){
        drawDiscards(discDict[(i + playerOrder ) % 4], i);
    }
});

socket.on('drawSets', function(setDict){
    for (var i=0; i<4; i++){
        drawSets(setDict[(i + playerOrder) % 4], i);
    }
});

socket.on('drawPlayerSet', function(player, sets){
    player = (player -  playerOrder + 4) % 4 ;
    drawSets(sets, player);;
});

socket.on('playerDraw', function(tile){
    playerDraw(tile)
});

socket.on('blindDraw', function(player){
    player = (player - playerOrder + 4) % 4 ;
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

socket.on('playerWin', function(playerName, tile, hand, pointDict){
    hideWin()
    playerWin(playerName, tile, hand, pointDict)
});

window.onload = function(){
    socket.emit('connected_to_game', roomID);
    setInitial();
}
