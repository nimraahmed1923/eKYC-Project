from face_recognition_module import recognize_face
import os

known_faces_dir = os.path.join("dataset", "faces")
test_image_path = os.path.join("test_faces", "test_face.jpg")

result = recognize_face(test_image_path, known_faces_dir)

if result:
    print(f"Face matched with: {result}")
else:
    print("No matching face found.")