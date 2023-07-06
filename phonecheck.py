import re


def validate_phone_number(number):
    pattern = "^\\+?[1-9][0-9]{7,14}$"
    if not re.fullmatch(pattern, number):
        return False

    return True
