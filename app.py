from flask import Flask, render_template
from flask_socketio import SocketIO

from utils.image import process_base64_encoded_image
from utils.detection import detect_face_v2
from utils.recognition import recognise_v2
from utils.store import record_attendace
from utils.encoder import stringify

app = Flask(__name__)
app.static_folder = "static"
socketio = SocketIO(app)


@app.route("/")
def home():
    return render_template("home.html")


@socketio.on("take-attendance")
def take_attendance(message):
    image = process_base64_encoded_image(message)
    face_points = detect_face_v2(image)
    output = recognise_v2(image)
    data = {
        "image": message,
        "output": output,
        "points": face_points,
    }
    socketio.emit("recieve-attendance", {"data": stringify(data)})


@socketio.on("store-attendace")
def store_attendance(message):
    record_attendace(message)


@socketio.on("connect")
def connect():
    socketio.emit("connect", {"data": "Connected"})


@socketio.on("disconnect")
def disconnect():
    print("Client disconnected")


if __name__ == "__main__":
    socketio.run(app, debug=True)