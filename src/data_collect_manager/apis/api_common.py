import re
from marshmallow import ValidationError


def character_validate(data):
    """ 使用不可な文字が含まれていないか検証 """

    pattern = re.compile("[a-zA-Z0-9-]+")
    if not pattern.fullmatch(data):
        raise ValidationError("Invalid character used.")
