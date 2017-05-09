import psycopg2
import configparser
import getpass
import hashlib
import sys


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

    def user_authorize(self):
        print('Choose your role:')
        print('1. Student')
        print('2. Teacher')
        print('3. Administrator')

        self.user_role = None
        while self.user_role not in ('1', '2', '3'):
            self.user_role = input('? ')
        self.user_role = int(self.user_role)

        user_login = input('Login: ')
        user_password = getpass.getpass('Password: ')

        if self.user_role == 1:
            self.db_execute('SELECT user_id, student_id FROM users_students WHERE login = %s AND PASSWORD = %s;', user_login, user_password)
        elif self.user_role == 2:
            self.db_execute('SELECT user_id, teacher_id FROM users_teachers WHERE login = %s AND PASSWORD = %s;', user_login, user_password)
        elif self.user_role == 3:
            self.db_execute('SELECT user_id FROM users_admins WHERE login = %s AND PASSWORD = %s;', user_login, user_password)

        result = self.cursor.fetchall()
        if not len(result):
            print('Incorrect login or password')
            exit(0)

        self.user_id = result[0][0]
        if self.user_role == 1:
            self.student_id = result[0][1]
        elif self.user_role == 2:
            self.teacher_id = result[0][1]

    def db_execute(self, query, *data):
        try:
            self.cursor.execute(query, data)
        except psycopg2.IntegrityError as e:
            raise e
        except psycopg2.Error as e:
            print('Database failure:', e.pgerror, file=sys.stderr)
            exit(3)

    def __init__(self):
        self.connection = self.cursor = None
        self.db_connect()

        self.user_role = self.user_id = self.teacher_id = self.student_id = None
        self.user_authorize()

    def __del__(self):
        self.connection.close()
