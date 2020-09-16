import os
from io import BytesIO
from tempfile import SpooledTemporaryFile

import fastjsonschema
import pytest
from fastjsonschema import JsonSchemaException

face_info_validator = fastjsonschema.compile({
    'type': 'object',
    'properties': {
        'data': {
            'type': "array",
            'items': {
               'type': "object",
               'properties': {
                   'bounding_box': {
                       'type': "object",
                       'properties': {
                           'left': {'type': "integer"},
                           'top': {'type': "integer"},
                           'right': {'type': "integer"},
                           'bottom': {'type': "integer"}
                       },
                       'required': ["left", "top", "right", "bottom"]
                   },
                   'face_points': {
                       'type': "array",
                       'items': {
                           'type': "object",
                           'properties': {
                               'x': {'type': "integer"},
                               'y': {'type': "integer"}
                           },
                           'required': ["x", "y"]
                       }
                   }
               },
               'required': ["bounding_box", "face_points"]
            },
        },
    },
    'required': ["data"],
    'additionalProperties': False
})

generic_error_validator = fastjsonschema.compile({
    'type': 'object',
    'properties': {
        'error': {'type': "string"}
    },
    'required': ["error"],
    'additionalProperties': False
})


form_error_validator = fastjsonschema.compile({
    'type': 'object',
    'properties': {'error': {
        'type': "object",
        'properties': {
            'field_errors': {
                'type': "object",
                'patternProperties': {
                    '.*': {
                        'type': "array",
                        'items': {'type': "string"}
                    }
                }
            },
            'non_field_error': {'type': "string"}
        },
        'required': ["field_errors", "non_field_error"],
    }},
    'required': ["error"],
    'additionalProperties': False
})


def test_face_info_endpoint(image_path, redis_client, client, monkeypatch):
    monkeypatch.setattr("face_recognizer.web.views.redis_client", redis_client)

    # Нормальная работа сервиса
    redis_client.flushall()
    with open(os.path.join(image_path, "face.jpg"), "rb") as f:
        response = client.post("/1.0/face-info", content_type="multipart/form-data", data={
            'image': (BytesIO(f.read()), "face.jpg")
        })
        try:
            face_info_validator(response.json)
        except JsonSchemaException:
            pytest.fail("Incorrect response data schema")
        else:
            assert response.json['data'][0]['bounding_box']['left'] != 0
            assert response.json['data'][2]['face_points'][2]['x'] != 0

    redis_client.flushall()
    with open(os.path.join(image_path, "face.bmp"), "rb") as f:
        response = client.post("/1.0/face-info", content_type="multipart/form-data", data={
            'image': (BytesIO(f.read()), "face.bmp")
        })
        try:
            face_info_validator(response.json)
        except JsonSchemaException:
            pytest.fail("Incorrect response data schema")

    redis_client.flushall()
    with open(os.path.join(image_path, "non_faces.jpg"), "rb") as f:
        response = client.post("/1.0/face-info", content_type="multipart/form-data", data={
            'image': (BytesIO(f.read()), "non_faces.jpg")
        })
        try:
            face_info_validator(response.json)
        except JsonSchemaException:
            pytest.fail("Incorrect response data schema")

    # Ошибка отсутствия изображения
    redis_client.flushall()
    with open(os.path.join(image_path, "face.jpg"), "rb") as f:
        response = client.post("/1.0/face-info", content_type="multipart/form-data", data={
            'WRONG_FIELD_NAME': (BytesIO(f.read()), "face.jpg")
        })
        assert response.json['error']['field_errors']['image'][0] == "This field is required."

    response = client.post("/1.0/face-info")
    assert response.json['error']['field_errors']['image'][0] == "This field is required."

    # Ошибка с невалидным изображением
    redis_client.flushall()
    with open(os.path.join(image_path, "bullshit.jpg"), "rb") as f:
        response = client.post("/1.0/face-info", content_type="multipart/form-data", data={
            'image': (BytesIO(f.read()), "bullshit.jpg")
        })
        assert response.json['error']['field_errors']['image'][0] == \
            "This file is not image, must be 8bit gray or RGB image."

    # Ошибка с пустым "изображением"
    redis_client.flushall()
    with open(os.path.join(image_path, "empty.jpg"), "rb") as f:
        response = client.post("/1.0/face-info", content_type="multipart/form-data", data={
            'image': (BytesIO(f.read()), "empty.jpg")
        })
        assert response.json['error']['field_errors']['image'][0] == "File is empty."

    # Ошибка чтения изображения
    redis_client.flushall()

    def errored_read(*args, **kwargs):
        raise OSError("Oops")

    with monkeypatch.context() as m:
        m.setattr(SpooledTemporaryFile, "read", errored_read)

        with open(os.path.join(image_path, "face.jpg"), "rb") as f:
            response = client.post("/1.0/face-info", content_type="multipart/form-data", data={
                'image': (BytesIO(f.read()), "face.jpg")
            })
            assert response.json['error']['field_errors']['image'][0] == "File is broken."

    # Отдан неверный формат
    redis_client.flushall()

    def errored_recognize(*args, **kwargs):
        return [{
            'bounding_box': {
                'top': 33,
                'left': 12,
                'bottom': 21,
                'right': 444
            },
            'face_points': [{
                'x': 3,
                'y': "STRING!"
            }]
        }]

    with monkeypatch.context() as m:
        m.setattr('face_recognizer.web.views.recognize', errored_recognize)

        with open(os.path.join(image_path, "face.jpg"), "rb") as f:
            response = client.post("/1.0/face-info", content_type="multipart/form-data", data={
                'image': (BytesIO(f.read()), "face.jpg")
            })
            assert "Response body does not conform to specification" in response.json['error']


def test_generic_error_api(image_path, client):
    with open(os.path.join(image_path, "face.jpg"), "rb") as f:
        response = client.post("/1.0/WRONG_URL!!!", content_type="multipart/form-data", data={
            'image': (BytesIO(f.read()), "face.jpg")
        })
        try:
            generic_error_validator(response.json)
        except JsonSchemaException:
            pytest.fail("Incorrect response data schema")
        else:
            assert response.status_code == 404


def test_form_error_api(image_path, client):
    with open(os.path.join(image_path, "face.jpg"), "rb") as f:
        response = client.post("/1.0/face-info", content_type="multipart/form-data", data={
            'WRONG_FIELD_NAME': (BytesIO(f.read()), "face.jpg")
        })
        try:
            form_error_validator(response.json)
        except JsonSchemaException:
            pytest.fail("Incorrect response data schema")


def test_huge_post_body_size_api(image_path, client, monkeypatch):
    with monkeypatch.context() as m:
        m.setitem(client.application.config, "MAX_CONTENT_LENGTH", 15)

        with open(os.path.join(image_path, "face.jpg"), "rb") as f:
            response = client.post("/1.0/face-info", content_type="multipart/form-data", data={
                'image': (BytesIO(f.read()), "face.jpg")
            })
            try:
                generic_error_validator(response.json)
            except JsonSchemaException:
                pytest.fail("Incorrect response data schema")
            else:
                assert response.json['error'] == \
                    "Request Entity Too Large: The data value transmitted exceeds the capacity limit."
                assert response.status_code == 413


def test_method_not_allowed_api(image_path, client):
    with open(os.path.join(image_path, "face.jpg"), "rb"):
        response = client.get("/1.0/face-info")
        try:
            generic_error_validator(response.json)
        except JsonSchemaException:
            pytest.fail("Incorrect response data schema")
        else:
            assert response.json['error'] == \
                "Method Not Allowed: The method is not allowed for the requested URL."
            assert response.status_code == 405


def test_unexpected_error_api(image_path, client, monkeypatch):
    def errored_recognize(*args, **kwargs):
        raise ValueError("Oops")

    with monkeypatch.context() as m:
        m.setattr("face_recognizer.web.views.recognize", errored_recognize)

        with open(os.path.join(image_path, "face.jpg"), "rb") as f:
            response = client.post("/1.0/face-info", content_type="multipart/form-data", data={
                'image': (BytesIO(f.read()), "face.jpg")
            })
            try:
                generic_error_validator(response.json)
            except JsonSchemaException:
                pytest.fail("Incorrect response data schema")
            else:
                assert response.json['error'] == "Internal Server Error: Unexpected error occurred."
                assert response.status_code == 500
