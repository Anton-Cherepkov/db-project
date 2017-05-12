# пароль, логин (для учителя) == a, a

# Меню учителя:

# 1. Классное руководство (у ученика 2473 есть какие то оценки) (id первого предмета == 46, полезно запускать на id = 55)
# 2. Посмотреть список учеников своего класса
# 3. Посмотреть список предметов
# 4. Выставление и просмотр оценок (не работаит)
# 5. Расписание
# 0. Назад

# Классное руководство (1.):
# 1.2 Посмотреть оценки ученика (у ученика 2473 есть какие то оценки)
# 1.3 Посмотреть оценки по предмету (id первого предмета == 46, полезно запускать на id = 55)
# 0. Назад

# Посмотреть оценки конкретного ученика (1.2):
# 1.2.1 Посмотреть все оценки
# 2.2.2 Выбрать период (ввести начальную и конечную даты)

# Посмотреть оценки по конкретному предмету
# Ввести id ученика, период времени
#
#
#
#
#
#
#
#

#
#
from session import Session, Role
from entry_student import Student
from entry_class import Class
from entry_subject import Subject
from colors import Color
from utils import read_date, print_wrong_format, print_wrong_format_

import datetime


class TeacherInteract:
    def __init__(self, session):
        self.session = session
        self.teacher_id = session.teacher_id
        self.db_execute = session.db_execute
        self.cursor = session.cursor
        self.fetchall = session.cursor.fetchall
        self.my_class_str = self.class_str()
        self.my_class_id = self.class_id()
        self.list_students = self.get_ids_students()
        self.list_days = ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота',
                          'Вся неделя']

    def handler_menu_teacher(self):
        assert self.session.user_role == Role.TEACHER, 'Role check failed'

        while True:
            print(Color.BLUE, end='')
            print('### Меню учителя ###')
            print('1. Классное руководство')
            print('2. Посмотреть список учеников своего класса')
            print('3. Посмотреть список предметов')
            print('5. Расписание')
            print('0. Выход')
            print(Color.RESET, end='')

            option = None
            while option not in ('0', '1', '2', '3', '4', '5'):
                option = input('? ')
            if option == '0':
                break

            if option == '1':
                self.class_management()
            elif option == '2':
                self.show_students()
            elif option == '3':
                self.show_subjects()
            elif option == '5':
                self.interact_schedule()

    def class_management(self):
        while True:
            print(Color.BLUE, end='')
            print('### Классное руководство ###')
            print('1. Посмотреть оценки ученика')
            print('2. Посмотреть оценки по предмету')
            print('0. Назад')
            print(Color.RESET, end='')
            option = None
            while option not in ('0', '1', '2'):
                option = input('? ')
            if option == '0':
                break
            if option == '1':
                self.show_marks_of_student()
            elif option == '2':
                self.show_marks_for_subject()

    def show_marks(self, table, id_kind, id_val):
        if id_kind == 'subject_id':
            another_id_kind = 'student_id'
        else:
            another_id_kind = 'subject_id'
        while True:
            print(Color.BLUE, end='')
            print('1. Посмотреть все оценки')
            print('2. Выбрать период')
            print('0. Назад')
            print(Color.RESET, end='')
            option = None
            while option not in ('0', '1', '2'):
                option = input('? ')
            if option == '0':
                return
            if option == '2':
                print(
                    'Выберите период, за который хотите узнать оценки.\n' +
                    'Вводите начальную и конечную дату в формате ГГГГ-ММ-ДД'
                )
                begin_date = read_date('Введите начальную дату: ')
                end_date = read_date('Введите конечную дату: ') + ' 23:59:59'
            if option == '2':
                s = "SELECT * from marks WHERE {0} = {1} AND time >= '{2}' AND time <= '{3}' ORDER BY {4}, time;".format(
                        id_kind, id_val, begin_date, end_date, another_id_kind)
                self.db_execute(
                   s
                )
            else:
                s = 'SELECT * from marks WHERE {0} = {1} ORDER BY {2}, time;'.format(
                        id_kind, id_val, another_id_kind)
                self.db_execute(
                    s
                )
                # print(s)
            result = self.fetchall()
            if len(result) == 0:
                if option == '1':
                    print('Оценок пока нет')
                else:
                    print('Нет оценок за выбранный период')
                continue
            # print('opa13')
            if table == 'students':
                cur_student = Student(self.session, id_val)
                print('Оценки ученика ' + cur_student.get('name_last'), cur_student.get('name_first'),
                      cur_student.get('name_middle') + ':')
                cur_subject_id = -1
                for i in range(len(result)):
                    if result[i][4] != cur_subject_id:
                        cur_subject_id = result[i][4]
                        cur_subject = Subject(self.session, result[i][4])
                        print('\n' + cur_subject.get('name') + ':')
                    print(result[i][5].date().isoformat(), result[i][5].time().strftime('%H:%M'), 'Оценка:',
                          result[i][1])
            elif table == 'subjects':
                cur_subject = Subject(self.session, id_val)
                print('Оценки по предмету ' + cur_subject.get('name') + ':')
                # print('opa14')
                cnt = 0
                cur_student_id = -1
                for i in range(len(result)):
                    if result[i][3] not in self.list_students:
                        continue
                    cnt += 1
                    if result[i][3] != cur_student_id:
                        cur_student_id = result[i][3]
                        cur_student = Student(self.session, cur_student_id)
                        print('\n' + cur_student.get('name_last'), cur_student.get('name_first'),
                              cur_student.get('name_middle') + ':')
                    print(result[i][5].date().isoformat(), result[i][5].time().strftime('%H:%M'), 'Оценка:',
                          result[i][1])
                if cnt == 0:
                    print('Оценок пока нет')

    def show_marks_for_subject(self):
        subject_id = self.read_id('предмета')
        # print('opa12')
        self.show_marks('subjects', 'subject_id', subject_id)

    def show_marks_of_student(self):
        student_id = self.read_id('ученика')
        self.show_marks('students', 'student_id', student_id)

    def read_id(self, obj):
        while True:
            obj_id = input('Введите id {0} '.format(obj))
            try:
                obj_id = int(obj_id)
            except ValueError:
                print(Color.RED, end='')
                print('Ожидалось число')
                print(Color.RESET, end='')
                continue
            # print('opa11')
            if obj == 'ученика':
                # print('opa10')
                self.db_execute(
                    'SELECT class_id FROM students WHERE student_id = %s',
                    obj_id
                )
            elif obj == 'предмета':
                # print('opa9')
                self.db_execute(
                    'SELECT subject_id FROM subjects WHERE subject_id = %s',
                    obj_id
                )
            result = self.fetchall()
            assert len(result) <= 1, 'чета много объектов с одним id(('
            if len(result) == 0:
                print_wrong_format('Неверный id')
                continue
            if obj == 'ученика':
                if result[0][0] != self.my_class_id:
                    print(Color.RED, end='')
                    print('Ученик учится не в Вашем классе')
                    print(Color.RESET, end='')
                    continue
            return obj_id

    def interact_schedule(self):
        while True:
            print(Color.BLUE, end='')
            print('### Узнать расписание ###')
            for i in range(1, 8):
                print(i, '. ', self.list_days[i], sep='')
            print('0. Назад')
            print(Color.RESET, end='')
            option = None
            while option not in ('0', '1', '2', '3', '4', '5', '6', '7'):
                option = input('? ')
            if option == '0':
                break
            self.show_schedule(int(option))

    def show_schedule(self, day):
        if day == 7:
            for i in range(1, 7):
                self.show_schedule(i)
        else:
            print(self.list_days[day] + ':')
            self.db_execute(
                'SELECT * FROM schedule WHERE teacher_id = %s AND day = %s ORDER BY time_begin',
                self.teacher_id, day
            )
            result = self.fetchall()
            if len(result) == 0:
                print('В этот день у Вас нет уроков\n')
                return
            num = 1
            for row in result:
                cur_sub = Subject(self.session, row[1])
                name_sub = cur_sub.get('name')
                cur_class = Class(self.session, row[2])
                name_class = str(cur_class.get('class_number')) + cur_class.get('class_letter')
                time_begin = row[5].strftime('%H:%M')
                dt = datetime.datetime.combine(datetime.date.today(), row[5]) + row[6]
                print(str(num) + '.', name_sub + ',', name_class, time_begin, '-', dt.time().strftime('%H:%M'))
                num += 1
            print()

    def get_ids_students(self):
        self.db_execute(
            'SELECT student_id FROM students WHERE class_id = %s;',
            self.my_class_id
        )
        result = self.fetchall()
        ans = []
        for el in result:
            ans.append(el[0])
        return ans

    def show_students(self):
        print('Список учеников {0} класса:'.format(self.my_class_str))
        self.db_execute(
            'SELECT student_id, name_last, name_first, name_middle FROM students WHERE class_id = %s;',
            self.my_class_id
        )
        result = self.fetchall()
        print_result(result)

    def show_subjects(self):
        print('Список предметов:')
        self.db_execute(
            'SELECT subject_id, name FROM subjects;'
        )
        result = self.fetchall()
        print_result(result)

    def class_str(self):
        self.db_execute(
            'SELECT class_number, class_letter FROM classes WHERE teacher_id = %s;',
            self.teacher_id
        )
        result = self.fetchall()
        assert len(result) == 1, 'чета много класснух у одного класса((('
        return str(result[0][0]) + result[0][1]

    def class_id(self):
        self.db_execute(
            'SELECT class_id FROM classes WHERE teacher_id = %s;',
            self.teacher_id
        )
        result = self.fetchall()
        assert len(result) == 1, 'чета много класснух у одного класса((('
        return result[0][0]


def print_result(lst):
    for row in lst:
        for i in range(len(row)):
            if i == 0:
                print('[id:', str(row[i]) + ']', end=' ')
            else:
                print(row[i], end=' ')
        print()


# сделать больше оценок
# сделать меньше учеников в классе
# сделать меньше уроков (либо добавить учителей, которые не класснухи, но ведут уроки [ето вроде лучше])
