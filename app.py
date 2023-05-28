from flask import Flask, render_template
from flask_socketio import SocketIO

from utils.image import process_base64_encoded_image, crop_faces
from utils.detection import detect_face
from utils.recognition import recognise

app = Flask(__name__)
app.static_folder = "static"
socketio = SocketIO(app)


@app.route("/")
def home():
    return render_template("homev3.html")


@socketio.on("take-attendance")
def take_attendance(message):
    image = process_base64_encoded_image(message)
    face_points = detect_face(image)
    faces = crop_faces(image, face_points)
    output = recognise(faces)
    data = {'image': message, 'output': output}
    socketio.emit("recieve-attendance", {"data": data})


@socketio.on("connect")
def connect():
    socketio.emit("connect", {"data": "Connected"})


@socketio.on("disconnect")
def disconnect():
    print("Client disconnected")


if __name__ == "__main__":
    socketio.run(app, debug=True)
    # app.run(debug=True)
