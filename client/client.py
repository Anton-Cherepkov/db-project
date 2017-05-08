import psycopg2
import hashlib
import getpass
import configparser
import sys


def load_config():
    try:
        config_parser = configparser.ConfigParser()
        config_parser.read('config.ini')
        db_config = dict()
        db_config['db_host'] = config_parser.get('db', 'db_host')
        db_config['db_port'] = config_parser.get('db', 'db_port')
        db_config['db_name'] = config_parser.get('db', 'db_name')
        db_config['db_user'] = config_parser.get('db', 'db_user')
        db_config['db_password'] = config_parser.get('db', 'db_password')
        return db_config
    except configparser.Error as e:
        print('Incorrect config.ini:', e.message, file=sys.stderr)
        exit(1)


def db_connect(db_config):
    try:
        connection = psycopg2.connect(host=db_config['db_host'], port=db_config['db_port'], dbname=db_config['db_name'], user=db_config['db_user'], password=db_config['db_password'])
        return connection
    except psycopg2.Error:
        print('Connection to database failed', file=sys.stderr)
        exit(2)


def db_execute(cursor, query, data = None):
    try:
        if data is None or not len(data):
            cursor.execute(query)
        else:
            cursor.execute(query, data)
    except psycopg2.IntegrityError as e:
        raise e
    except psycopg2.Error as e:
        print('execute() failed:', e.pgerror, file=sys.stderr)
        exit(3)


def user_authorize(cursor):
    user_config = dict()
    user_config['user_role'] = None

    print('Choose your role:')
    print('1. Student')
    print('2. Teacher')
    print('3. Administrator')
    while user_config['user_role'] not in ('1', '2', '3'):
        user_config['user_role'] = input('? ')
    user_config['user_role'] = int(user_config['user_role'])

    user_login = input('Login: ')
    user_password = getpass.getpass('Password: ')

    if user_config['user_role'] == 1:
        db_execute(cursor, 'SELECT user_id, student_id FROM users_students WHERE login = %s AND password = %s;', (user_login, user_password))
    elif user_config['user_role'] == 2:
        db_execute(cursor, 'SELECT user_id, teacher_id FROM users_teachers WHERE login = %s AND password = %s;', (user_login, user_password))
    elif user_config['user_role'] == 3:
        db_execute(cursor, 'SELECT user_id FROM users_admins WHERE login = %s AND password = %s;', (user_login, user_password))

    result = cursor.fetchall()
    if not len(result):
        print('Incorrect login or password')
        exit(0)

    user_config['user_id'] = result[0][0]
    if user_config['user_role'] == 1:
        user_config['student_id'] = result[0][1]
    elif user_config['user_role'] == 2:
        user_config['teacher_id'] = result[0][1]

    return user_config


def main():
    connection = db_connect(load_config())
    cursor = connection.cursor()
    user_config = user_authorize(cursor)
    print(user_config)

if __name__ == "__main__":
    main()
