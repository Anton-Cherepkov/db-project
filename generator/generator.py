import psycopg2
import hashlib
from random import randint
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


def parse_file(s):
    f = open(s, 'r')
    lst = f.readlines()
    lst[:] = (value for value in lst if value != '\n')
    for i in range(len(lst)):
        lst[i] = lst[i].replace('\n', '').replace(' ', '').replace('\t', '')
    return lst


def phone_number():
    s = '8'
    # 8 999 260 74 95
    for i in range(10):
        s += str(randint(1, 9))
    return s


def rand_el(lst):
    return lst[randint(0, len(lst) - 1)]


def main():
    connection = db_connect(load_config())
    cursor = connection.cursor()
    connection.set_isolation_level(0)

    man_names = parse_file('man_names.txt')
    lady_names = parse_file('lady_names.txt')
    man_last_names = parse_file('man_last_names.txt')
    lady_last_names = []
    for el in man_last_names:
        lady_last_names.append(el + 'а')
    man_middle_names = parse_file('man_middle_names.txt')
    lady_middle_names = parse_file('lady_middle_names.txt')
    subjects = open('subjects_list.txt').readlines()
    for i in range(len(subjects)):
        subjects[i] = subjects[i].replace('\n', '')

    cursor.execute('DELETE FROM subjects_teachers')
    cursor.execute('DELETE FROM schedule')
    cursor.execute('DELETE FROM marks')
    cursor.execute('DELETE FROM students')
    cursor.execute('DELETE FROM classes')

    cursor.execute('DELETE FROM teachers')
    for i in range(33):
        sex = randint(1, 2)
        if sex == 1:
            name = rand_el(man_names)
            middle_name = rand_el(man_middle_names)
            last_name = rand_el(man_last_names)
        else:
            name = rand_el(lady_names)
            middle_name = rand_el(lady_middle_names)
            last_name = rand_el(lady_last_names)
        s = 'INSERT INTO teachers(name_first, name_middle, name_last, phone) VALUES'
        s += ' (' + "'" + name + "'" + ', ' + "'" + middle_name + "'" + ', ' + "'" + last_name + "'" + ', ' + "'" + \
             phone_number() + "'" + ');'
        cursor.execute(s)

    print('ok')

    cursor.execute('SELECT * FROM teachers')
    rows = cursor.fetchall()
    pos = rows[0][0]
    cursor.execute('DELETE FROM classes')
    for i in range(1, 12):
        for j in range(0, 3):
            s = 'INSERT INTO classes(class_number, class_letter, teacher_id) VALUES ('
            lt = chr(ord('а') + j)
            s += str(i) + ', ' + "'" + lt + "'" + ', ' + str(pos) + ');'
            pos += 1
            cursor.execute(s)

    print('ok')

    cursor.execute('DELETE FROM subjects')
    for el in subjects:
        s = "INSERT INTO subjects(name) VALUES ('{0}');".format(el)
        cursor.execute(s)

    print('ok')

    cursor.execute('DELETE FROM students')
    cursor.execute('SELECT * FROM classes')
    rows = cursor.fetchall()
    start_class_id = rows[0][0]

    for i in range(start_class_id, start_class_id + 33):
        for cnt_students in range(randint(23, 27)):
            sex = randint(1, 2)
            if sex == 1:
                name = rand_el(man_names)
                middle_name = rand_el(man_middle_names)
                last_name = rand_el(man_last_names)
            else:
                name = rand_el(lady_names)
                middle_name = rand_el(lady_middle_names)
                last_name = rand_el(lady_last_names)
            s = "INSERT INTO students (name_first, name_middle, name_last, class_id, phone) VALUES ('{0}', '{1}', '{2}', {3}, '{4}');".format(
                name, middle_name, last_name, i, phone_number())
            cursor.execute(s)

    print('ok')

    cursor.execute('DELETE FROM schedule')
    cursor.execute('SELECT * FROM subjects_teachers')
    rows_st = cursor.fetchall()

    cursor.execute('SELECT * FROM classes')
    rows = cursor.fetchall()
    start_class_id = rows[0][0]

    times = ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00']

    for day in range(1, 1 + 5):
        for class_id in range(start_class_id, start_class_id + 33):
            for lesson in range(randint(5, 7)):
                time_begin = times[lesson]
                el = rand_el(rows_st)
                subject_id = el[0]
                teacher_id = el[1]
                s = "INSERT INTO schedule (subject_id, class_id, teacher_id, day, time_begin, time_duration) VALUES ({0}, {1}, {2}, {3}, '{4}', '{5}');".format(
                    subject_id, class_id, teacher_id, day, time_begin, '40 minutes')
                cursor.execute(s)

    print('ok')

    cursor.execute('DELETE from marks')
    cursor.execute('SELECT * FROM schedule')
    rows = cursor.fetchall()

    for i in range(0, len(rows), 2):
        el = rows[i]
        day = el[4]
        time = el[5].isoformat()
        date = '2017-05-'
        if 7 + day < 10:
            date += '0'
        date += str(7 + day) + ' ' + time

        q = 'SELECT * FROM students WHERE class_id = {0}'.format(el[2])
        cursor.execute(q)
        rows_students = cursor.fetchall()
        rand_student = rand_el(rows_students)[0]
        s = "INSERT INTO marks (value, teacher_id, student_id, subject_id, time) VALUES ({0}, {1}, {2}, {3}, '{4}');".format(
            randint(2, 5), el[3], rand_student, el[1], date
        )
        cursor.execute(s)

    print('ok')

    cursor.execute('DELETE FROM users_admins')
    cursor.execute("INSERT INTO users_admins (login, password) VALUES ('admin', 'admin')")

if __name__ == "__main__":
    main()
