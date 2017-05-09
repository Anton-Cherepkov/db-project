class Schedule:
    schedule_id = 'schedule_id'
    subject_id = 'subject_id'
    class_id = 'class_id'
    teacher_id = 'teacher_id'
    day = 'day'
    time_begin = 'time_begin'
    time_duration = 'time_duration'
    columns = [subject_id, class_id, teacher_id, day, time_begin, time_duration]

    def __init__(self, session, id):
        self.session = session
        self.id = id

    def get(self, column):
        assert column in Schedule.columns, 'Unknown column name'

        self.session.db_execute('SELECT ' + column + ' FROM schedule WHERE schedule_id = %s;', self.id)
        return self.session.cursor.fetchall()[0][0]

    def set(self, column, value):
        assert column in Schedule.columns, 'Unknown column name'

        self.session.db_execute('UPDATE schedule SET ' + column + ' = %s WHERE schedule_id = %s;', value, self.id)
