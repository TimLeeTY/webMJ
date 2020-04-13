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

var tileDict = [[0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7], [0, 8], [0, 9], [1, 1], [1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [1, 7], [1, 8], [1, 9], [2, 1], [2, 2], [2, 3], [2, 4], [2, 5], [2, 6], [2, 7], [2, 8], [2, 9], [3, 1], [3, 2], [3, 3], [3, 4], [4, 1], [4, 2], [4, 3]]
var suitLabel = ['Dots', 'Bamboo', 'Numbers']
var honorLabel = [['East', 'South', 'West', 'North'], ['Red', 'Green', 'White']]

for (var i = 0; i<tileDict.length; i++) {
    var tileEle = document.getElementById(Math.floor(i/9)+'-'+(i%9))
    drawTile(tileEle, i)
}
