class Schedule:
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
        assert column in Schedule.columns, 'Unknown column name'

        self.session.db_execute('SELECT ' + column + ' FROM marks WHERE mark_id = %s;', self.id)
        return self.session.cursor.fetchall()[0][0]

    def set(self, column, value):
        assert column in Schedule.columns, 'Unknown column name'

        self.session.db_execute('UPDATE marks SET ' + column + ' = %s WHERE mark_id = %s;', value, self.id)
