import os

from werkzeug.datastructures import FileStorage

from face_recognizer.recognizer import recognize


def test_recognize(image_path):
    with open(os.path.join(image_path, "face.jpg"), "rb") as f:
        result = recognize(FileStorage(f))
        assert len(result) == 5
        assert len(result[0]["face_points"]) == 5

    with open(os.path.join(image_path, "face.bmp"), "rb") as f:
        result = recognize(FileStorage(f))
        assert len(result) == 1

    with open(os.path.join(image_path, "non_faces.jpg"), "rb") as f:
        result = recognize(FileStorage(f))
        assert len(result) == 0
