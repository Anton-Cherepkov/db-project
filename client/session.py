import psycopg2
import configparser
import getpass
import hashlib
import sys
from enum import Enum
from entry_teacher import Teacher
from entry_student import Student

from colors import Color


class Role(Enum):
    STUDENT = 1
    TEACHER = 2
    ADMINISTRATOR = 3

    @staticmethod
    def get_role(role):
        role = str(role)
        assert role in ('1', '2', '3'), 'Unknown role'

        if role is '1':
            return Role.STUDENT
        if role is '2':
            return Role.TEACHER
        return Role.ADMINISTRATOR


class Session:
    def db_connect(self):
        try:
            config_parser = configparser.ConfigParser()
            config_parser.read('config.ini')
            db_config = dict()
            db_config['db_host'] = config_parser.get('db', 'db_host')
            db_config['db_port'] = config_parser.get('db', 'db_port')
            db_config['db_name'] = config_parser.get('db', 'db_name')
            db_config['db_user'] = config_parser.get('db', 'db_user')
            db_config['db_password'] = config_parser.get('db', 'db_password')
        except configparser.Error as e:
            print('Incorrect config.ini:', e.message, file=sys.stderr)
            exit(1)

        try:
            self.connection = psycopg2.connect(host=db_config['db_host'],
                                          port=db_config['db_port'],
                                          dbname=db_config['db_name'],
                                          user=db_config['db_user'],
                                          password=db_config['db_password'])
            self.cursor = self.connection.cursor()
        except psycopg2.Error:
            print('Connection to database failed', file=sys.stderr)
            exit(2)

    @staticmethod
    def encrypt_password(password):
        return password

    def user_authorize(self):
        print(Color.BLUE, end='')
        print('Выберите роль:')
        print('1. Ученик')
        print('2. Учитель')
        print('3. Администратор')
        print('0. Выход')
        print(Color.RESET, end='')

        self.user_role = None
        while self.user_role not in ('0', '1', '2', '3'):
            self.user_role = input('? ')

        if self.user_role is '0':
            exit(0)
        self.user_role = Role.get_role(self.user_role)

        user_login = input('Логин: ')
        user_password = Session.encrypt_password(getpass.getpass('Пароль: ')) # необходимо добавить шифрование

        if self.user_role is Role.STUDENT:
            self.db_execute('SELECT user_id, student_id FROM users_students WHERE login = %s AND PASSWORD = %s;', user_login, user_password)
        elif self.user_role is Role.TEACHER:
            self.db_execute('SELECT user_id, teacher_id FROM users_teachers WHERE login = %s AND PASSWORD = %s;', user_login, user_password)
        elif self.user_role is Role.ADMINISTRATOR:
            self.db_execute('SELECT user_id FROM users_admins WHERE login = %s AND PASSWORD = %s;', user_login, user_password)

        result = self.cursor.fetchall()
        if not result:
            print(Color.RED, end='')
            print('Неправильная пара логин/пароль')
            print(Color.RESET, end='')
            exit(0)

        self.user_id = result[0][0]
        if self.user_role is Role.STUDENT:
            self.student_id = result[0][1]
        elif self.user_role is Role.TEACHER:
            self.teacher_id = result[0][1]

        self.hello_message()

    def db_execute(self, query, *data):
        try:
            self.cursor.execute(query, data)
        except psycopg2.IntegrityError as e:
            raise e
        except psycopg2.Error as e:
            print('Database failure:', e.pgerror, file=sys.stderr)
            exit(3)

    def hello_message(self):
        print(Color.CYAN, end='')
        if self.user_role is Role.ADMINISTRATOR:
            print('Добро пожаловать')

        if self.user_role is Role.TEACHER:
            teacher = Teacher(self, self.teacher_id)
            print('Добро пожаловать, ', end='')
            print(' '.join((teacher.get(Teacher.name_first), teacher.get(Teacher.name_last),)))

        if self.user_role is Role.STUDENT:
            student = Student(self, self.student_id)
            print('Добро пожаловать, ', end='')
            print(' '.join((student.get(Student.name_first), student.get(Student.name_last),)))
        print(Color.RESET, end='')

    def bye_message(self):
        print(Color.CYAN, end='')
        if self.user_role is Role.ADMINISTRATOR:
            print('До свидания')

        if self.user_role is Role.TEACHER:
            teacher = Teacher(self, self.teacher_id)
            print('До свидания, ', end='')
            print(' '.join((teacher.get(Teacher.name_first), teacher.get(Teacher.name_last),)))

        if self.user_role is Role.STUDENT:
            student = Student(self, self.student_id)
            print('До свидания, ', end='')
            print(' '.join((student.get(Student.name_first), student.get(Student.name_last),)))
        print(Color.RESET, end='')

    def __init__(self):
        self.connection = self.cursor = None
        self.db_connect()

        self.user_role = self.user_id = self.teacher_id = self.student_id = None
        self.user_authorize()

    def __del__(self):
        self.bye_message()