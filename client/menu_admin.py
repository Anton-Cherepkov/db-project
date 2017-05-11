from session import Session, Role
from entry_student import Student
from entry_class import Class
import psycopg2
import psycopg2.extensions


# Админское меню
# 1. Управление учениками
#
# 2. Управление классами
# 3. Управление расписанием (?)
# 4. Выход
def menu_admin(session):
    assert session.user_role is Role.ADMINISTRATOR, 'Role check failed'

    while True:
        print('### Меню администратора ###')
        print('1. Управление учениками')
        print('2. Управление учителями')
        print('3. Управление классами')
        print('4. Управление расписанием')
        print('0. Выход')

        option = None
        while option not in ('0', '1', '2', '3', '4'):
            option = input('? ')
        if option is '0':
            break

        if option is '1':
            menu_control_students(session)


def menu_control_students(session):
    while True:
        print('### Управление учениками ###')
        print('1. Список учеников')
        print('2. Редактировать ученика')
        print('3. Добавить ученика')
        print('0. Назад')

        option = None
        while option not in ('0', '1', '2', '3'):
            option = input('? ')
        if option is '0':
            break

        if option is '1':
            show_students(session)
        elif option is '2':
            edit_student(session)


def show_students(session):
    print('### Список учеников ###')

    session.db_execute('SELECT student_id, name_first, name_middle, name_last, class_id FROM students')
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
    print('### Редактирование ученика ###')

    student_id = input('Введите id ученика: ')
    try:
        student_id = int(student_id)
    except ValueError:
        print('Ожидалось число')
        return None

    session.db_execute('SELECT student_id FROM students WHERE student_id = %s', student_id)
    if not session.cursor.fetchall():
        print('Ученик с id ' + str(student_id) + ' не существует')
        return None

    student = Student(session, student_id)
    print('Фамилия:', str(student.get(Student.name_last)))
    print('Имя:', str(student.get(Student.name_first)))
    name_middle = student.get(Student.name_middle)
    print('Отчество:', str(name_middle) if name_middle else 'netu)')
    phone = student.get(Student.phone)
    print('Телефон:', str(phone) if phone else '')
    student_class = Class(session, int(student.get(Student.class_id)))
    print('Класс:', str(student_class.get(Class.class_number))
          + str(student_class.get(Class.class_letter)))

    while True:
        print('Выберите действие:')
        print('1. Изменить телефон')
        print('2. Изменить класс')
        print('3. Создать аккаунт в системе')
        print('0. Назад')
        option = None
        while option not in ('0', '1', '2', '3'):
            option = input('? ')
        if option is '0':
            return None

        if option is '1':
            phone = input('Новый телефон: ')
            if len(phone) > 30:
                print('Длина телефона не может быть более 30 символов')
                continue
            student.set(Student.phone, phone if len(phone) else None)
        elif option is '2':
            class_id = input('Введите id класса: ')
            try:
                class_id = int(class_id)
            except ValueError:
                print('Ожидалось число')
                continue

            try:
                student.set(Student.class_id, class_id)
            except psycopg2.IntegrityError as err:
                if err.pgcode == '23503':  # foreign_key_violation
                    print('Класс с id ' + str(class_id) + ' не существует')
                    session.connection.rollback()
                    continue
                raise err
        elif option is '3':
            login = input('Введите логин нового аккаунта: ')
            password = Session.encrypt_password(input('Введите пароль нового аккаунта: '))
            if not password or not login:
                print('Пароль не может быть пустым')
                continue
            try:
                session.db_execute(
                    'INSERT INTO users_students (login, password, student_id) VALUES (%s, %s, %s)', login, password, student.id)
            except psycopg2.IntegrityError as err:
                if err.pgcode == '23505':
                    if err.diag.constraint_name == 'users_students_student_id_key':
                        print('У данного ученика уже существует аккаунт')
                    elif err.diag.constraint_name == 'users_students_login_key':
                        print('Этот логин уже занят')
                    else:
                        raise err
                    session.connection.rollback()
                    continue
                raise err
        session.connection.commit()

# Управление классами
# 1. Список классов
# 2. Посмотреть класс
# 3. Изменить классного классного руководителя
# 4. Создать класс
