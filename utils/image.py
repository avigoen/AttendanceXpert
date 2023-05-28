import base64, cv2
import numpy as np


def process_base64_encoded_image(base64_image):
    image_data = base64_image.split(',')[1]
    decoded_img = base64.b64decode(image_data)
    nparr = np.frombuffer(decoded_img, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image


def crop_faces(image, points):
    faces = [image[y : y + h, x : x + w] for (x, y, w, h) in points]
    return faces
