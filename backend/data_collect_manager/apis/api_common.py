import re
from marshmallow import ValidationError


def character_validate(data):
    """使用不可な文字が含まれていないか検証"""

    pattern = re.compile("^[0-9a-zA-Z-]+$")
    if not pattern.fullmatch(data):
        raise ValidationError("Invalid character used.")
