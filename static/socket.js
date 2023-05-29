$(document).ready(function () {

    function updateClock() {
        var now = new Date(), // current date
            months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']; // you get the idea
        time = now.getHours() + ':' + now.getMinutes() + ":" + now.getSeconds(), // again, you get the idea

            // a cleaner way than string concatenation
            date = [now.getDate(),
            months[now.getMonth()],
            now.getFullYear()].join(' ');

        // set the content of the element with the ID time to the formatted string
        document.getElementById('time').innerHTML = [date, time].join(' / ');

        // call this function again in 1000ms
        setTimeout(updateClock, 1000);
    }

    updateClock()

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
        data = JSON.parse(response['data'])
        output = data['output']
        faces = data['points']

        var img = new Image
        img.onload = function () {
            context.clearRect(0, 0, canvas.width, canvas.height);
            context.drawImage(img, 0, 0, canvas.width, canvas.height)

            for (let i = 0; i < faces.length; i++) {
                [top_point, right_point, bottom_point, left_point] = faces[i]
                context.lineWidth = 2;
                context.strokeStyle = 'red';
                context.beginPath();
                context.rect(top_point, left_point, (bottom_point - top_point), (right_point - left_point));
                context.stroke();

                context.font = 'bold 16px Arial';
                context.fillStyle = 'yellow';
                context.fillText(output[i]['label'], top_point, left_point - 10);

                imageElement.src = canvas.toDataURL('image/png');

            }
            socket.emit('store-attendace', output)
        }
        img.src = data['image']

    });

    // startStream()
    function broadcast_video() {
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