from flask_redis import FlaskRedis

from face_recognizer.web import make_flask_app

redis_client = FlaskRedis(make_flask_app())
