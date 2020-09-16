from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import ValidationError

from face_recognizer.web.api_formatter import CustomFormError


class FaceImageForm(CustomFormError):
    class Meta:
        csrf = False

    magic_numbers = {
        'jpg': b"\xff\xd8\xff\xe0",
        'jpeg': b"\xff\xd8\xff\xe0",
        'bmp': b"\x42\x4d",
    }
    max_header_len = max([len(magic_number) for magic_number in magic_numbers.values()])

    image = FileField("image", validators=[
        FileRequired(),
        # TODO: убрать это, если расширения неважны
        FileAllowed(magic_numbers.keys(), "This file is not image, must be 8bit gray or RGB image.")
    ])

    def validate_image(self, field):
        try:
            file_header = field.data.stream.read(self.max_header_len)
        except OSError:
            raise ValidationError("File is broken.")
        else:
            if not file_header:
                raise ValidationError("File is empty.")

        if not any(map(lambda magic_number: magic_number in file_header, self.magic_numbers.values())):
            raise ValidationError("This file is not image, must be 8bit gray or RGB image.")
