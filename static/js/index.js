function draw(imgData){
    var b64imgData = btoa(imgData); //Binary to ASCII, where it probably stands for
    var img = new Image();
    img.src = "data:image/jpeg;base64," + b64imgData;
    document.body.appendChild(img); //or append it to something else, just an example
}