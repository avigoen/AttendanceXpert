import face_recognition, pickle
import numpy as np

known_face_encoding = None
with open("static/embeddings.pkl", "rb") as f:
    known_face_encoding = pickle.load(f)

known_faces_names = None
with open("static/labels.pkl", "rb") as f1:
    known_faces_names = pickle.load(f1)


def _detect_person_v2(frame):
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    face_names = []
    outputs = []
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encoding, face_encoding)
        face_distance = face_recognition.face_distance(
            known_face_encoding, face_encoding
        )
        best_match_index = np.argmin(face_distance)
        name = known_faces_names[best_match_index] if matches[best_match_index] else ""
        print(name, best_match_index)
        if name in known_faces_names:
            if best_match_index not in face_names:
                face_names.append(best_match_index)
                outputs.append(
                    {
                        "index": len(outputs),
                        "label": face_names[-1],
                        "name": known_faces_names[face_names[-1]],
                    }
                )

    if not len(outputs):
        outputs.append({"index": -1, "label": -1, "name": "Unknown"})

    return outputs


def recognise_v2(image):
    return _detect_person_v2(image)
