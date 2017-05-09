class Student:
    student_id = 'student_id'
    name_first = 'name_first'
    name_middle = 'name_middle'
    name_last = 'name_last'
    class_id = 'class_id'
    phone = 'phone'
    columns = [name_first, name_middle, name_last, class_id, phone]

    def __init__(self, session, id):
        self.session = session
        self.id = id

    def get(self, column):
        assert column in Student.columns, 'Unknown column name'

        self.session.db_execute('SELECT ' + column + ' FROM students WHERE student_id = %s;', self.id)
        return self.session.cursor.fetchall()[0][0]

    def set(self, column, value):
        assert column in Student.columns, 'Unknown column name'

        self.session.db_execute('UPDATE students SET ' + column + ' = %s WHERE student_id = %s;', value, self.id)
