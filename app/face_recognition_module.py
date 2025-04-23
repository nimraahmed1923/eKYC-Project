import face_recognition
import os

def load_known_faces(known_faces_dir):
    known_encodings = []
    known_names = []

    for filename in os.listdir(known_faces_dir):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            path = os.path.join(known_faces_dir, filename)
            image = face_recognition.load_image_file(path)
            encodings = face_recognition.face_encodings(image)

            if encodings:
                known_encodings.append(encodings[0])
                name = os.path.splitext(filename)[0]
                known_names.append(name)

    return known_encodings, known_names


def recognize_face(test_image_path, known_faces_dir):
    known_encodings, known_names = load_known_faces(known_faces_dir)

    test_image = face_recognition.load_image_file(test_image_path)
    test_encodings = face_recognition.face_encodings(test_image)

    if not test_encodings:
        return None

    test_encoding = test_encodings[0]
    results = face_recognition.compare_faces(known_encodings, test_encoding)
    distances = face_recognition.face_distance(known_encodings, test_encoding)

    if True in results:
        best_match_index = distances.argmin()
        return known_names[best_match_index]
    else:
        return None