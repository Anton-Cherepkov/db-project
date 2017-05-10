class Mark:
    mark_id = 'mark_id'
    value = 'value'
    teacher_id = 'teacher_id'
    student_id = 'student_id'
    subject_id = 'subject_id'
    time = 'time'
    columns = [value, teacher_id, student_id, subject_id, time]

    def __init__(self, session, id):
        self.session = session
        self.id = id

    def get(self, column):
        assert column in Mark.columns, 'Unknown column name'

        self.session.db_execute('SELECT ' + column + ' FROM marks WHERE mark_id = %s;', self.id)
        return self.session.cursor.fetchall()[0][0]

    def set(self, column, value):
        assert column in Mark.columns, 'Unknown column name'

        self.session.db_execute('UPDATE marks SET ' + column + ' = %s WHERE mark_id = %s;', value, self.id)

    def set(self, column, value):
        assert column in Mark.columns, 'Unknown column name'

        self.session.db_execute('UPDATE schedule SET ' + column + ' = %s WHERE schedule_id = %s;', value, self.id)

    @staticmethod
    def add(session, *args):  # usage: add((Student.name_first, 'Антон'), (Student.name_middle, 'Юрьевич'))
        for arg in args:
            assert arg[0] in Mark.columns, 'Unknown column name'

        columns = ', '.join(list(map(lambda x: x[0], args)))
        values = list(map(lambda x: x[1], args))
        query = 'INSERT INTO marks (' + columns + ') VALUES (' + ('%s, ' * len(args))[:-2:] + ') RETURNING mark_id;'
        session.db_execute(query, *values)

        id = session.cursor.fetchall()[0][0]
        return Mark(session, id)
