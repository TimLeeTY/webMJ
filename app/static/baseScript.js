function preloadImages() {
    if (!preloadImages.list) {
        preloadImages.list = [];
    }
    var list = preloadImages.list;
    for (var i = 0; i < tileDict.length; i++) {
        var img = new Image();
        var t = tileDict[i];
        var url = "https://webmj-assets.s3.us-east-2.amazonaws.com/"+t[0]+"-"+t[1]+"-.svg";
        img.onload = function() {
            var index = list.indexOf(this);
            if (index !== -1) {
                // remove image from the array once it's loaded
                // for memory consumption reasons
                list.splice(index, 1);
            }
        }
        list.push(img);
        img.src = url;
    }
}

var tileDict = [[0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7], [0, 8], [0, 9], [1, 1], [1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [1, 7], [1, 8], [1, 9], [2, 1], [2, 2], [2, 3], [2, 4], [2, 5], [2, 6], [2, 7], [2, 8], [2, 9], [3, 1], [3, 2], [3, 3], [3, 4], [4, 1], [4, 2], [4, 3]];

window.onload = function(){
    if (typeof setInitial == "function"){
        socket.emit('connected_to_game', roomID);
        setInitial();
    }
    else{
        preloadImages();
    }
}
