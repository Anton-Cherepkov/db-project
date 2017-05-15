from session import Session, Role
from operator import itemgetter
from entry_student import Student
from entry_class import Class
from entry_subject import Subject
from entry_mark import Mark
from colors import Color
from utils import read_date, print_wrong_format, print_wrong_format_, read_date_returning_parts
import calendar
import datetime


def get_nums(cnt):
    res = []
    for i in range(cnt):
        res.append(str(i + 1))
    res.append('0')
    return res


class TeacherInteract:
    def __init__(self, session):
        self.session = session
        self.teacher_id = session.teacher_id
        self.db_execute = session.db_execute
        self.cursor = session.cursor
        self.fetchall = session.cursor.fetchall
        self.my_class_str = None
        self.my_class_id = None
        self.list_students = None
        self.have_own_classes = self.check_own_class()
        self.class_id_to_str = self.set_class_id_to_str()
        self.class_id_to_pair = self.get_class_id_to_pair()
        self.subject_id_to_name = self.get_subject_id_to_name()
        self.list_days = ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота',
                          'Вся неделя']

    def handler_menu_teacher(self):
        assert self.session.user_role == Role.TEACHER, 'Role check failed'

        while True:
            print(Color.BLUE, end='')
            print('### Меню учителя ###')
            print('1. Классное руководство')
            print('2. Управление оценками')
            print('3. Расписание')
            print('0. Выход')
            print(Color.RESET, end='')

            option = None
            while option not in ('0', '1', '2', '3'):
                option = input('? ')
            if option == '0':
                break

            if option == '1':
                self.class_management()
            elif option == '2':
                self.interact_marks()
            elif option == '3':
                self.interact_schedule()

    def interact_marks(self):
        self.session.connection.set_isolation_level(0)
        while True:
            print(Color.BLUE, end='')
            print('### Управление оценками ###')
            print('1. Добавить оценку')
            print('2. Редактирование и проссмотр оценок')
            print('0. Выход')
            print(Color.RESET, end='')

            option = None
            while option not in ('0', '1', '2', '3'):
                option = input('? ')
            if option == '0':
                return
            if option == '1':
                self.add_marks()
            elif option == '2':
                self.change_and_show_marks()
            elif option == '3':
                pass

    def change_and_show_marks(self):
        print('Выберите класс:')
        self.db_execute(
            'SELECT class_id FROM schedule WHERE teacher_id = %s;',
            self.teacher_id
        )
        all_classes = self.fetchall()
        all_classes = list(set(all_classes))
        if len(all_classes) == 0:
            print('Вы не ведете уроки ни у одного класса')
            return
        for i in range(len(all_classes)):
            all_classes[i] = (all_classes[i][0], self.class_id_to_pair[all_classes[i][0]])
        all_classes.sort(key=itemgetter(1))
        for i in range(len(all_classes)):
            print(i + 1, '. ', self.class_id_to_str[all_classes[i][0]], sep='')
        print('0. Выход')
        nums = get_nums(len(all_classes))
        option = None
        while option not in nums:
            option = input('? ')
        if option == '0':
            return
        class_id = all_classes[int(option) - 1][0]
        # print(class_id)
        self.db_execute(
            'SELECT subject_id FROM schedule WHERE teacher_id = %s AND class_id = %s;',
            self.teacher_id, class_id
        )
        all_subs = self.fetchall()
        all_subs = list(set(all_subs))
        if len(all_subs) == 0:
            print('Вы не ведете уроки у этого класса')
            return
        print('Выберите предмет:')
        for i in range(len(all_subs)):
            print(i + 1, '. ', self.subject_id_to_name[all_subs[i][0]], sep='')
        print('0. Выход')
        nums = get_nums(len(all_subs))
        option = None
        while option not in nums:
            option = input('? ')
        if option == '0':
            return
        subject_id = all_subs[int(option) - 1][0]
        # print(subject_id)
        print('Выберите ученика: ')
        self.db_execute(
            'SELECT * FROM students WHERE class_id = %s;',
            class_id
        )
        all_students = self.fetchall()
        for i in range(len(all_students)):
            print(i + 1, '. ', all_students[i][3], ' ', all_students[i][1], ' ', all_students[i][2], sep='')
        print('0. Выход')
        nums = get_nums(len(all_students))
        option = None
        while option not in nums:
            option = input('? ')
        if option == '0':
            return
        option = int(option)
        student_id = all_students[option - 1][0]
        print('Оценки ученика {0} по предмету {1}'.format(all_students[option - 1][3] + ' ' + all_students[option - 1][1] +
                                                           ' ' + all_students[option - 1][2], self.subject_id_to_name[subject_id]))
        self.db_execute(
            'SELECT * FROM marks WHERE teacher_id = %s AND student_id = %s AND subject_id = %s',
            self.teacher_id, student_id, subject_id
        )
        all_marks = self.fetchall()
        if len(all_marks) == 0:
            print('Оценок пока нет')
            return
        print('Выберите оценку для редактирования: ')
        for i in range(len(all_marks)):
            print(str(i + 1) + '.', all_marks[i][5].date().isoformat(), all_marks[i][5].time().strftime('%H:%M'), 'Оценка:',
                  all_marks[i][1])
        print('0. Выход')
        nums = get_nums(len(all_marks))
        option = None
        while option not in nums:
            option = input('? ')
        if option == '0':
            return
        option = int(option)
        mark_id = all_marks[option-1][0]
        # print(mark_id)
        print('Введите новое значение оценки. \nВведите 0 чтобы удалить оценку.')
        option = None
        while option not in ('0', '2', '3', '4', '5'):
            option = input('? ')
            # print('>', option, '<')
        if option == '0':
            self.db_execute(
                'DELETE FROM marks WHERE mark_id = %s',
                mark_id
            )
            print('Оценка удалена')
            return
        option = int(option)
        my_mark = Mark(self.session, mark_id)
        # print('opa')
        my_mark.set('value', option)
        print('Оценка изменена, новая оценка:')
        self.db_execute(
            'SELECT * FROM marks WHERE mark_id = %s',
            mark_id
        )
        new_mark = self.fetchall()
        if len(new_mark) == 0:
            print('Упс, что-то пошло не так, попробуйте еще раз(')
            return
        print(new_mark[0][5].date().isoformat(), new_mark[0][5].time().strftime('%H:%M'), 'Оценка:',
              new_mark[0][1])

    def add_marks(self):
        dates = read_date_returning_parts('Введите дату для выставления оценки')
        if dates == -1:
            return
        day, month, year = dates[1][0], dates[1][1], dates[1][2]
        week_day = (calendar.weekday(year, month, day) + 1) % 7
        '''
          print(self.list_days[day] + ':')
            self.db_execute(
                'SELECT name, time_begin, time_duration '
                'FROM subjects '
                'INNER JOIN '
                '(SELECT * FROM schedule WHERE teacher_id = %s AND day = %s) AS subq '
                'USING (subject_id) '
                'ORDER BY time_begin;',
                self.teacher_id, day
            )
            result = self.fetchall()
            if not result:
                print('В этот день у Вас нет уроков')
                return
            for row in result:
                subject_name = row[0]
                time_begin = row[1].strftime('%H:%M')
                time_end = (datetime.datetime.combine(datetime.date.today(), row[1]) + row[2]).strftime('%H:%M')
                print(time_begin, '-', time_end, subject_name)
        '''
        self.db_execute(
            'SELECT * FROM schedule WHERE teacher_id = %s AND day = %s ORDER BY time_begin;',
            self.teacher_id, week_day
        )
        result = self.fetchall()
        self.db_execute(
            'SELECT name, time_begin, time_duration '
            'FROM subjects '
            'INNER JOIN '
            '(SELECT * FROM schedule WHERE teacher_id = %s AND day = %s) AS subq '
            'USING (subject_id) '
            'ORDER BY time_begin;',
            self.teacher_id, week_day
        )
        result2 = self.fetchall()
        if len(result2) == 0:
            print('В этот день у Вас нет уроков\n')
            return
        print('Выберите урок:')
        num = 1
        #for row in result:
        #    cur_sub = Subject(self.session, row[1])
        #    name_sub = cur_sub.get('name')
        #    cur_class = Class(self.session, row[2])
        #    name_class = str(cur_class.get('class_number')) + cur_class.get('class_letter')
        #    time_begin = row[5].strftime('%H:%M')
        #    dt = datetime.datetime.combine(datetime.date.today(), row[5]) + row[6]
        #    print(str(num) + '.', name_sub + ',', name_class, time_begin, '-', dt.time().strftime('%H:%M'))
        #    num += 1
        for row in result2:
            subject_name = row[0]
            time_begin = row[1].strftime('%H:%M')
            time_end = (datetime.datetime.combine(datetime.date.today(), row[1]) + row[2]).strftime('%H:%M')
            print(str(num) + '.', time_begin, '-', time_end, subject_name)
            num += 1
        print('0. Назад')
        nums = []
        cnt_lessons = len(result)
        for i in range(cnt_lessons + 1):
            nums.append(str(i))
        option = None
        while option not in nums:
            option = input('? ')
        if option == '0':
            return
        row = result[int(option) - 1]
        cur_sub = Subject(self.session, row[1])
        name_sub = cur_sub.get('name')
        cur_class = Class(self.session, row[2])
        name_class = str(cur_class.get('class_number')) + cur_class.get('class_letter')
        time_begin = row[5].strftime('%H:%M')
        dt = datetime.datetime.combine(datetime.date.today(), row[5]) + row[6]
        self.db_execute(
            'SELECT student_id, name_last, name_first, name_middle FROM students WHERE class_id = %s;',
            result[int(option) - 1][2]
        )
        result = self.fetchall()
        print('Выберите ученика:')
        for i in range(len(result)):
            print(str(i + 1) + '.', result[i][1], result[i][2], result[i][3])
        print('0. Выход')
        nums = get_nums(len(result))
        option = None
        while option not in nums:
            option = input('? ')
            # print('>', option, '<')
        if option == '0':
            return
        option = int(option)
        student_id = result[option - 1][0]
        # print('Список учеников', name_class, 'класса')
        # print_result(result)
        # student_id = input('Введите id ученика ')
        '''
        try:
            student_id = int(student_id)
        except ValueError:
            print_wrong_format('Ожидалось число')
            return
        flag = 0
        for el in result:
            if el[0] == student_id:
                flag = 1
                break
        if flag == 0:
            print_wrong_format('Неверный id')
            return
        '''
        mark_value = input('Введите оценку от 2 до 5 ')
        try:
            mark_value = int(mark_value)
        except ValueError:
            print_wrong_format('Ожидалось число')
            return
        if mark_value < 2 or mark_value > 5:
            print_wrong_format('Неверное значение')
            return
        self.db_execute(
            "INSERT INTO marks (value, teacher_id, student_id, subject_id, time) VALUES (%s, %s, %s, %s, %s) RETURNING mark_id;",
            mark_value, self.teacher_id, student_id, cur_sub.id, datetime.datetime(year, month, day, row[5].hour, row[5].minute)
        )
        result = self.fetchall()
        print('Оценка добавлена [id:', str(result[0][0]) + ']')

    def class_management(self):
        if self.have_own_classes == 0:
            print('Вы не являетесь классным руководителем')
            return
        self.choose_class()
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
                print('Выберите период, за который хотите узнать оценки.')
                begin_date = read_date('Введите начальную дату: ')
                if begin_date == -1:
                    return
                end_date = read_date('Введите конечную дату: ') + ' 23:59:59'
                if end_date == -1:
                    return
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
            student_id_to_names = self.get_student_id_to_names(self.my_class_id)
            if table == 'students':
                cur_student = Student(self.session, id_val)
                print('Оценки ученика ' + cur_student.get('name_last'), cur_student.get('name_first'),
                      cur_student.get('name_middle') + ':')
                cur_subject_id = -1
                for i in range(len(result)):
                    if result[i][4] != cur_subject_id:
                        cur_subject_id = result[i][4]
                        #cur_subject = Subject(self.session, result[i][4])
                        #print('\n' + cur_subject.get('name') + ':')
                        print('\n' + self.subject_id_to_name[cur_subject_id] + ':')
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
                        #cur_student = Student(self.session, cur_student_id)
                        #print('\n' + cur_student.get('name_last'), cur_student.get('name_first'),
                         #     cur_student.get('name_middle') + ':')
                        print('\n' + student_id_to_names[cur_student_id][0], student_id_to_names[cur_student_id][1],
                              student_id_to_names[cur_student_id][2])
                    print(result[i][5].date().isoformat(), result[i][5].time().strftime('%H:%M'), 'Оценка:',
                          result[i][1])
                if cnt == 0:
                    print('Оценок пока нет')

    def get_student_id_to_names(self, class_id):
        self.db_execute(
            'SELECT * FROM students WHERE class_id = %s',
            class_id
        )
        res = dict()
        result = self.fetchall()
        for el in result:
            res[el[0]] = (el[3], el[1], el[2])
        return res

    def show_marks_for_subject(self):
        # subject_id = self.read_id('предмета')
        subject_id = self.choose_subject()
        if subject_id == -1:
            return
        # print('opa12')
        self.show_marks('subjects', 'subject_id', subject_id)

    def choose_student(self):
        print('Выберите ученика:')
        self.db_execute(
            'SELECT * FROM students WHERE class_id = %s ORDER BY name_last;',
            self.my_class_id
        )
        all_students = self.fetchall()
        for i in range(len(all_students)):
            print(i + 1, '. ', all_students[i][3], ' ', all_students[i][1], ' ', all_students[i][2], sep='')
        print('0. Назад')
        nums = get_nums(len(all_students))
        option = None
        while option not in nums:
            option = input('? ')
        if option == '0':
            return -1
        option = int(option)
        return all_students[option - 1][0]

    def choose_subject(self):
        print('Выберите предмет:')
        self.db_execute(
            'SELECT * FROM subjects;'
        )
        all_subs = self.fetchall()
        for i in range(len(all_subs)):
            print(i + 1, '. ', all_subs[i][1], sep='')
        print('0. Назад')
        nums = get_nums(len(all_subs))
        option = None
        while option not in nums:
            option = input('? ')
        if option == '0':
            return -1
        option = int(option)
        return all_subs[option - 1][0]

    def show_marks_of_student(self):
        student_id = self.choose_student()
        # student_id = self.read_id('ученика')
        if student_id == -1:
            return
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
                return -1
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
                return -1
            if obj == 'ученика':
                if result[0][0] != self.my_class_id:
                    print(Color.RED, end='')
                    print('Ученик учится не в Вашем классе')
                    print(Color.RESET, end='')
                    return -1
            return obj_id

    def interact_schedule(self):
        while True:
            print(Color.BLUE, end='')
            print('### Узнать расписание ###')
            for i in range(0, 8):
                print(i + 1, '. ', self.list_days[i], sep='')
            print('0. Назад')
            print(Color.RESET, end='')
            option = None
            while option not in ('0', '1', '2', '3', '4', '5', '6', '7', '8'):
                option = input('? ')
            if option == '0':
                break
            self.show_schedule(int(option) - 1)

    def show_schedule(self, day):
        if day == 7:
            for i in range(0, 7):
                self.show_schedule(i)
                print()
        else:
            print(self.list_days[day] + ':')
            self.db_execute(
                'SELECT name, time_begin, time_duration, class_id '
                'FROM subjects '
                'INNER JOIN '
                '(SELECT * FROM schedule WHERE teacher_id = %s AND day = %s) AS subq '
                'USING (subject_id) '
                'ORDER BY time_begin;',
                self.teacher_id, day
            )
            result = self.fetchall()
            if not result:
                print('В этот день у Вас нет уроков')
                return
            for row in result:
                subject_name = row[0]
                time_begin = row[1].strftime('%H:%M')
                time_end = (datetime.datetime.combine(datetime.date.today(), row[1]) + row[2]).strftime('%H:%M')
                class_str = self.class_id_to_str[row[3]]
                print(time_begin, '-', time_end, subject_name, class_str)

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
            'SELECT student_id, name_last, name_first, name_middle FROM students WHERE class_id = %s ORDER BY name_last;',
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
        assert len(result) <= 1, 'чета много класснух у одного класса((('
        if len(result) == 0:
            return ''
        return str(result[0][0]) + result[0][1]

    def class_id(self):
        self.db_execute(
            'SELECT class_id FROM classes WHERE teacher_id = %s;',
            self.teacher_id
        )
        result = self.fetchall()
        assert len(result) <= 1, 'чета много класснух у одного класса((('
        if len(result) == 0:
            return -1
        return result[0][0]

    def check_own_class(self):
        self.db_execute(
            'SELECT class_id FROM classes WHERE teacher_id = %s;',
            self.teacher_id
        )
        result = self.fetchall()
        if len(result) == 0:
            return 0
        return 1

    def set_class_id_to_str(self):
        res = dict()
        self.db_execute(
            'select * from classes;'
        )
        result = self.fetchall()
        for el in result:
            res[el[0]] = str(el[1]) + el[2]
        return res

    def get_class_id_to_pair(self):
        res = dict()
        self.db_execute(
            'select * from classes;'
        )
        result = self.fetchall()
        for el in result:
            res[el[0]] = (el[1], el[2])
        return res

    def get_subject_id_to_name(self):
        res = dict()
        self.db_execute(
            'select * from subjects;'
        )
        result = self.fetchall()
        for el in result:
            res[el[0]] = el[1]
        return res

    def choose_class(self):
        self.db_execute(
            'SELECT class_id, class_number, class_letter FROM classes WHERE teacher_id = %s;',
            self.teacher_id
        )
        result = self.fetchall()
        cnt = len(result)
        assert cnt >= 1
        print('Выберите класс:')
        nums = get_nums(cnt)
        for i in range(cnt):
            print(i + 1, '. ', result[i][1], result[i][2], ' класс', sep='')
        print('0. Назад')
        option = None
        while option not in nums:
            option = input('? ')
        if option == '0':
            return
        option = int(option) - 1
        self.my_class_str = str(result[option][1]) + result[option][2]
        self.my_class_id = result[option][0]
        self.list_students = self.get_ids_students()


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
