from flask import json
from flask_wtf import FlaskForm
from werkzeug import Response
from wtforms import ValidationError


def problem_exception_handler(e):
    response = Response(json.dumps({'error': f"{e.title}: {e.detail}"}), 500, e.headers)
    response.content_type = "application/json"
    return response


def exception_handler(e):
    response = e.get_response()

    err_msg = f"{e.name}: {e.description}"
    response.data = json.dumps({'error': err_msg})
    response.content_type = "application/json"
    return response


class CustomFormError(FlaskForm):
    """
    Класс привносит свою структуру в ошибки формы
    Так же добавляются общие ошибки формы, для использования нужно в наследниках переопределить
    "validate_all" и кинуть "ValidationError"
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._non_field_error = ""

    def validate_all(self):
        """
        Метод - хук для наследников, поля получать из self._fields
        :return:
        """
        pass

    def validate(self, extra_validators=None):
        parent_validation = super().validate(extra_validators)

        try:
            self.validate_all()
        except ValidationError as e:
            self._non_field_error = str(e)
        return parent_validation

    def errors_to_dict(self):
        return {
            'error': {
                'field_errors': self.errors,
                'non_field_error': self._non_field_error
            }
        }
