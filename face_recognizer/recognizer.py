import dlib
import numpy
from PIL import Image
from dynaconf import settings
from werkzeug.datastructures import FileStorage


def recognize(image: FileStorage):
    """
    Распознает лица на картинке, возвращает информацию об обрамляющей рамке и некотором количестве
    точек внутри рамки
    :return: [{
        "bounding_box": {
          "bottom": 0,
          "left": 0,
          "right": 0,
          "top": 0
        },
        "face_points": [
          {
            "x": 0,
            "y": 0
          }
        ]
    }]
    """
    image_data = numpy.asarray(Image.open(image))

    face_detector = dlib.get_frontal_face_detector()
    dets = face_detector(image_data, 1)
    predictor = dlib.shape_predictor(settings.SHAPE_PREDICTOR_MODEL_PATH)

    result = []
    for d in dets:
        face_info = {
            'bounding_box': {},
            'face_points': []
        }

        face_info['bounding_box']['left'] = d.left()
        face_info['bounding_box']['top'] = d.top()
        face_info['bounding_box']['right'] = d.right()
        face_info['bounding_box']['bottom'] = d.bottom()

        shape = predictor(image_data, d)
        for i in range(min(shape.num_parts, settings.POINTS_PER_FACE)):
            face_info['face_points'].append({'x': shape.part(i).x, 'y': shape.part(i).y})

        result.append(face_info)
    return result
