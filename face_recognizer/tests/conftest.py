import logging.config
import os

import pytest
from dynaconf import settings
from fakeredis import FakeStrictRedis

from face_recognizer.config.setup_settings import configure_settings
from face_recognizer.web import make_flask_app

os.environ.setdefault("ENV_FOR_DYNACONF", "testing")


@pytest.fixture(scope="session")
def proj_settings():
    configure_settings()
    logging.config.dictConfig(settings.LOGGER)
    return settings


@pytest.fixture(scope="session")
def client(proj_settings):
    flask_app = make_flask_app()
    with flask_app.test_client() as cl:
        yield cl


@pytest.fixture(scope="function")
def redis_client():
    yield FakeStrictRedis()


@pytest.fixture(scope="session")
def image_path(proj_settings):
    return os.path.join(proj_settings.PROJECT_PATH, "tests", "images")
