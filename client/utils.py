from colors import Color

import calendar
import hashlib


def encrypt_password(password):
    return hashlib.sha256(password.encode() + b'25cdab54f934222f7699a29cfb6caf4a').hexdigest()


def read_date(message):
    while True:
        date = input(message)
        date_list = date.split('-')
        if len(date_list) != 3 or len(date) != 10:
            print_wrong_format()
            continue
        if len(date_list[0]) != 4 or len(date_list[1]) != 2 or len(date_list[2]) != 2:
            print_wrong_format()
            continue
        try:
            day = int(date_list[2])
            month = int(date_list[1])
            year = int(date_list[0])
        except ValueError:
            print_wrong_format()
            continue
        try:
            calendar.monthcalendar(year, month)
        except ValueError:
            print_wrong_format('Такой даты не существует')
            continue
        cnt_days = calendar.monthrange(year, month)[1]
        if day < 1 or day > cnt_days:
            print_wrong_format('Такой даты не существует')
            continue
        return date


def print_wrong_format(message='Неверный формат'):
    print(Color.RED, end='')
    print(message)
    print(Color.RESET, end='')


def print_wrong_format_():
    print(Color.RED, end='')
    print('Ожидалось число')
    print(Color.RESET, end='')