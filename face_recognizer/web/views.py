import hashlib
import logging
import traceback

from dynaconf import settings
from flask import request, json
from werkzeug.exceptions import InternalServerError

from face_recognizer.recognizer import recognize
from face_recognizer.web.cache import redis_client
from face_recognizer.web.forms import FaceImageForm

logger = logging.getLogger("face_recognizer")


def face_info():
    form = FaceImageForm(formdata=request.files)
    if not form.validate():
        return form.errors_to_dict()
    try:
        file_hash = hashlib.md5(form.image.data.stream.read()).hexdigest()
        cache_key = settings.CACHE.FACE_INFO_CACHE_KEY.format(file_hash)
        cached_response = redis_client.get(cache_key)
        if not cached_response:
            cached_response = recognize(form.image.data)
            redis_client.set(cache_key, json.dumps(cached_response),
                             settings.CACHE.FACE_INFO_CACHE_TIMEOUT)
        else:
            cached_response = json.loads(cached_response)
        return {'data': cached_response}
    except Exception:
        logger.error(traceback.format_exc())
        # Можно и подробную ошибку с трейсом отдавать (если вызывает внутренний сервис)
        raise InternalServerError(description="Unexpected error occurred.")
