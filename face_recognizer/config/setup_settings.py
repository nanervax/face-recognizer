import os

from dynaconf import settings


def configure_settings():
    os.environ.setdefault(
        "SETTINGS_FILE_FOR_DYNACONF",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.toml")
    )

    os.environ.setdefault(
        "SETTINGS_PROJECT_DIR",
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )

    os.environ.setdefault("ENVVAR_PREFIX_FOR_DYNACONF", "CONF")
    settings.configure()
