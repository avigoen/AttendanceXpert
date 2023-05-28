$(document).ready(function () {
    var socket = io.connect('http://127.0.0.1:5000');
    var video = document.getElementById('video');
    var canvas = document.createElement('canvas');
    var context = canvas.getContext('2d');

    // Function to handle successful video stream
    function handleVideoStream(stream) {
        video.srcObject = stream;
        video.play();
    }

    // Function to handle video capture error
    function handleVideoError(error) {
        console.log('Error accessing video stream:', error);
    }

    // Function to start the webcam stream
    function startStream() {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(handleVideoStream)
            .catch(handleVideoError);
    }

    // Function to stop the webcam stream
    function stopStream() {
        var mediaStream = video.srcObject;
        if (mediaStream) {
            var tracks = mediaStream.getTracks();
            tracks.forEach(function (track) {
                track.stop();
            });
        }
        video.srcObject = null;
    }

    socket.on('connect', function (response) {
        console.log(response);
    });
    socket.on('end_connection', () => {
        socket.disconnect();
    });

    socket.on('recieve-attendance', function (response) {
        var imageElement = document.getElementById('screenshot');
        data = response['data']
        imageElement.src = data['image'];
        console.log(data['output'])
    });

    // startStream()
    function broadcast_video(){
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Convert the canvas to base64 image
        var screenshot = canvas.toDataURL('image/png');
        socket.emit('take-attendance', screenshot);
    }

    startStream()
    document.getElementById('screenshot-btn').addEventListener('click', broadcast_video);
})