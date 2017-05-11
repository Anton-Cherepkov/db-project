from session import Session, Role
from entry_student import Student
from entry_class import Class

import psycopg2
import psycopg2.extensions

from enum import Enum
from termcolor import colored

from colors import Color


def menu_admin(session):
    assert session.user_role is Role.ADMINISTRATOR, 'Role check failed'

    while True:
        print(Color.BLUE, end='')
        print('### Меню администратора ###')
        print('1. Управление учениками')
        print('2. Управление учителями')
        print('3. Управление классами')
        print('4. Управление расписанием')
        print('0. Выход')
        print(Color.RESET, end='')

        option = None
        while option not in ('0', '1', '2', '3', '4'):
            option = input('? ')
        if option is '0':
            break

        if option is '1':
            menu_control_students(session)
        elif option is '2':
            menu_control_teachers(session)


def menu_control_students(session):
    while True:
        print(Color.BLUE, end='')
        print('### Управление учениками ###')
        print('1. Список учеников')
        print('2. Редактировать ученика')
        print('3. Добавить ученика')
        print('0. Назад')
        print(Color.RESET, end='')

        option = None
        while option not in ('0', '1', '2', '3'):
            option = input('? ')
        if option is '0':
            break

        if option is '1':
            show_students(session)
        elif option is '2':
            edit_student(session)
        elif option is '3':
            create_student(session)


def menu_control_teachers(session):
    while True:
        print(Color.BLUE, end='')
        print('### Управление учителями ###')
        print('1. Список учителей')
        print('2. Редактировать учителя')
        print('3. Добавить учителя')
        print('0. Назад')
        print(Color.RESET, end='')

        option = None
        while option not in ('0', '1', '2', '3'):
            option = input('? ')
        if option is '0':
            break

        if option is '1':
            show_teachers(session)
        '''elif option is '2':
            edit_teacher(session)
        elif option is '3':
            create_teacher(session)'''


# students
def show_students(session):
    print(Color.BLUE, end='')
    print('### Список учеников ###')
    print(Color.RESET, end='')

    session.db_execute('SELECT student_id, name_first, name_middle, name_last, class_id FROM students;')
    result = session.cursor.fetchall()
    for row in result:
        print('[id: ' + str(row[0]) + ']', end=' ')
        student_class = Class(session, int(row[4]))
        print('[' + str(student_class.get(Class.class_number)) + str(student_class.get(Class.class_letter)) + ']', end=' ')
        print(str(row[1]), end=' ')
        if row[2]:
            print(str(row[2]), end=' ')
        print(str(row[3]))


def edit_student(session):
    print(Color.BLUE, end='')
    print('### Редактирование ученика ###')
    print(Color.RESET, end='')

    student_id = input('Введите id ученика: ')
    try:
        student_id = int(student_id)
    except ValueError:
        print(Color.RED, end='')
        print('Ожидалось число')
        print(Color.RESET, end='')
        return None

    session.db_execute('SELECT student_id FROM students WHERE student_id = %s;', student_id)
    if not session.cursor.fetchall():
        print(Color.RED, end='')
        print('Ученик с id ' + str(student_id) + ' не существует')
        print(Color.RESET, end='')
        return None

    student = Student(session, student_id)
    print('Фамилия:', str(student.get(Student.name_last)))
    print('Имя:', str(student.get(Student.name_first)))
    name_middle = student.get(Student.name_middle)
    print('Отчество:', str(name_middle) if name_middle else '')
    phone = student.get(Student.phone)
    print('Телефон:', str(phone) if phone else '')
    student_class = Class(session, int(student.get(Student.class_id)))
    print('Класс:', str(student_class.get(Class.class_number))
          + str(student_class.get(Class.class_letter)))

    while True:
        print(Color.BLUE, end='')
        print('Выберите действие:')
        print('1. Изменить телефон')
        print('2. Изменить класс')
        print('3. Создать аккаунт в системе')
        print('4. Выгнать ученика')
        print('0. Назад')
        print(Color.RESET, end='')
        option = None
        while option not in ('0', '1', '2', '3', '4'):
            option = input('? ')
        if option is '0':
            return None

        if option is '1':
            phone = input('Новый телефон: ')
            if len(phone) > 30:
                print(Color.RED, end='')
                print('Длина телефона не может быть более 30 символов')
                print(Color.RESET, end='')
                continue
            student.set(Student.phone, phone if len(phone) else None)
            session.connection.commit()

        elif option is '2':
            class_id = input('Введите id класса: ')
            try:
                class_id = int(class_id)
            except ValueError:
                print(Color.RED, end='')
                print('Ожидалось число')
                print(Color.RESET, end='')
                continue

            try:
                student.set(Student.class_id, class_id)
            except psycopg2.IntegrityError as err:
                if err.pgcode == '23503':  # foreign_key_violation
                    print(Color.RED, end='')
                    print('Класс с id ' + str(class_id) + ' не существует')
                    print(Color.RESET, end='')
                    session.connection.rollback()
                    continue
                raise err
            session.connection.commit()

        elif option is '3':
            login = input('Введите логин нового аккаунта: ')
            password = Session.encrypt_password(input('Введите пароль нового аккаунта: '))
            if not password or not login:
                print(Color.RED, end='')
                print('Пароль/логин не могут быть пустыми')
                print(Color.RESET, end='')
                continue
            try:
                session.db_execute(
                    'INSERT INTO users_students (login, password, student_id) VALUES (%s, %s, %s)', login, password, student.id)
            except psycopg2.IntegrityError as err:
                if err.pgcode == '23505': # unique_violation
                    if err.diag.constraint_name == 'users_students_student_id_key':
                        print(Color.RED, end='')
                        print('У данного ученика уже существует аккаунт')
                        print(Color.RESET, end='')
                    elif err.diag.constraint_name == 'users_students_login_key':
                        print(Color.RED, end='')
                        print('Этот логин уже занят')
                        print(Color.RESET, end='')
                    else:
                        raise err
                    session.connection.rollback()
                    continue
                raise err

            session.connection.commit()
            print(Color.GREEN, end='')
            print('Аккаунт с логином', login, 'создан')
            print(Color.RESET, end='')

        elif option is '4':
            session.db_execute('DELETE FROM users_students WHERE student_id = %s;', student.id)
            session.db_execute('DELETE FROM students WHERE student_id = %s;', student.id)
            session.connection.commit()
            print(Color.GREEN, end='')
            print('Ученик изгнан')
            print(Color.RESET, end='')
            return None


def create_student(session):
    print(Color.BLUE, end='')
    print('### Добавление ученика ###')
    print(Color.RESET, end='')

    name_last = input('Фамилия: ')
    if not name_last:
        print(Color.RED, end='')
        print('Фамилия не может быть пустой')
        print(Color.RESET, end='')
        return None

    name_first = input('Имя: ')
    if not name_first:
        print(Color.RED, end='')
        print('Имя не может быть пустым')
        print(Color.RESET, end='')
        return None

    name_middle = input('Отчество: ')
    if not name_middle:
        name_middle = None

    phone = input('Телефон: ')
    if not phone:
        phone = None

    class_id = input('id класса: ')
    try:
        class_id = int(class_id)
    except ValueError:
        print(Color.RED, end='')
        print('Ожидалось число')
        print(Color.RESET, end='')

    student = None
    try:
        student = Student.add(session, (Student.name_first, name_first), (Student.name_last, name_last), (Student.name_middle, name_middle),
                (Student.phone, phone), (Student.class_id, class_id))
    except psycopg2.IntegrityError as err:
        if err.pgcode == '23503':
            print(Color.RED, end='')
            print('Класс с id ' + str(class_id) + ' не существует')
            print(Color.RESET, end='')
            session.connection.rollback()
            return None
        raise err

    print(Color.GREEN, end='')
    print('Ученик добавлен, id', student.id)
    print(Color.RESET, end='')


# teachers
def show_teachers(session):
    print(Color.BLUE, end='')
    print('### Список учителей ###')
    print(Color.RESET, end='')

    session.db_execute('SELECT teacher_id, name_first, name_middle, name_last FROM teachers;')
    result = session.cursor.fetchall()
    for row in result:
        print('[id: ' + str(row[0]) + ']', end=' ')
        print(str(row[1]), end=' ')
        if row[2]:
            print(str(row[2]), end=' ')
        print(str(row[3]))


# Управление классами
# 1. Список классов
# 2. Посмотреть класс
# 3. Изменить классного классного руководителя
# 4. Создать класс
