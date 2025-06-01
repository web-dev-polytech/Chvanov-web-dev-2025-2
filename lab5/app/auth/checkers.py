import re

def check_login(login: str) -> bool:
    if len(login) < 5:
        raise ValueError('Логин должен содержать не менее 5 символов')
    if not re.fullmatch(r'^[a-zA-Z0-9]+$', login):
        raise ValueError('Логин может содержать только латинские буквы и цифры')
    return True

def check_password(password: str) -> bool:
    allowed_special = r'~!?@#$%^&*_-+()[]{}><\/|"\'.:,;'
    allowed_letters = r'a-zA-Zа-яА-ЯёЁ'
    allowed_digits = r'0-9'
    allowed_special_escaped = re.escape(allowed_special)
    pattern = rf'^[{allowed_letters}{allowed_digits}{allowed_special_escaped}]+$'

    if len(password) < 8:
        raise ValueError('Пароль должен содержать не менее 8 символов')
    if len(password) > 128:
        raise ValueError('Пароль слишком длинный (максимум 128 символов)')
    if ' ' in password:
        raise ValueError('Пароль не должен содержать пробелов')
    if not (re.search(r'[A-ZА-ЯЁ]', password) and re.search(r'[a-zа-яё]', password)):
        raise ValueError('Пароль должен содержать хотя бы одну заглавную и одну строчную буквы (латинскую или кириллическую)')
    if not re.search(r'[0-9]', password):
        raise ValueError('Пароль должен содержать хотя бы одну арабскую цифру')
    if not re.fullmatch(pattern, password):
        raise ValueError('Пароль содержит недопустимые символы')
    return True