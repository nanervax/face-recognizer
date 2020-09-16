import logging.config

from connexion import ProblemException
from dynaconf import settings
import connexion

from face_recognizer.config.setup_settings import configure_settings
from face_recognizer.web.api_formatter import exception_handler, problem_exception_handler

configure_settings()
logging.config.dictConfig(settings.LOGGER)


def make_app():
    if make_app.app:
        return make_app.app

    app = connexion.FlaskApp(__name__, specification_dir="openapi/")
    app.add_error_handler(500, exception_handler)
    app.add_error_handler(404, exception_handler)
    app.add_error_handler(405, exception_handler)
    app.add_error_handler(413, exception_handler)
    app.add_error_handler(ProblemException, problem_exception_handler)
    make_app.app = app

    flask_app = app.app
    flask_app.config.from_object(settings.FLASK)

    if settings.FLASK.DEBUG:
        app.add_api("api.yaml", validate_responses=True)
    else:
        app.add_api("api.yaml")
    return app


make_app.app = None


def make_flask_app():
    return make_app().app
