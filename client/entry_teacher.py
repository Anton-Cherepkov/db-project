from psycopg2.extensions import AsIs

class Teacher:
    teacher_id = 'teacher_id'
    name_first = 'name_first'
    name_middle = 'name_middle'
    name_last = 'name_last'
    phone = 'phone'
    columns = [teacher_id, name_first, name_middle, name_last, phone]

    def __init__(self, session, id):
        self.session = session
        self.id = id

    def get(self, column):
        assert column in Teacher.columns, 'Unknown column name'

        self.session.db_execute('SELECT ' + column + ' FROM teachers WHERE teacher_id = %s;', self.id)
        return self.session.cursor.fetchall()[0][0]

    def set(self, column, value):
        assert column in Teacher.columns, 'Unknown column name'

        self.session.db_execute('UPDATE teachers SET ' + column + ' = %s WHERE teacher_id = %s;', value, self.id)