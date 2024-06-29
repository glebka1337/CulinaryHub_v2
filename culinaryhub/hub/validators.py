from django.core.exceptions import *
from .models import *
from django.contrib.auth.models import User


def validate_unique_username(value):
    if User.objects.filter(username=value).exists():
        raise ValidationError('Пользователь с таким именем уже существует')
    return value


def validate_unique_email(value):
    if User.objects.filter(email=value).exists():
        raise ValidationError('Пользователь с таким почтовым адресом уже существует')
    return value


def validate_russian_input(value):
    if any(char not in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ() ' for char in value):
        raise ValidationError('Вводите только русские буквы')


def validate_chars_only(value):
    if any(char.isdigit() for char in value):
        raise ValidationError('Вводите только буквы')


def validate_password(value):
    if len(value) < 8:
        raise ValidationError('Пароль должен содержать более 8 символов')
    if not any(char.isdigit() for char in value):
        raise ValidationError('Пароль должен содержать хотя бы одну цифру')
    if not any(char.islower() for char in value):
        raise ValidationError('Пароль должен содержать хотя бы одну строчную букву')
    if not any(char.isupper() for char in value):
        raise ValidationError('Пароль должен содержать хотя бы одну заглавную букву')
    if not any(char in '!@#$%^&*()_+-=' for char in value):
        raise ValidationError('Пароль должен содержать хотя бы один специальный символ')
    return value


def validate_image_size(value):
    if value.size > 5 * 1024 * 1024:
        raise ValidationError('Размер изображения не должен превышать 5 МБ')
    return value
