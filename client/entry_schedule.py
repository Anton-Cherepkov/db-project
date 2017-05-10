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

    @staticmethod
    def add(session, *args):  # usage: add((Student.name_first, 'Антон'), (Student.name_middle, 'Юрьевич'))
        for arg in args:
            assert arg[0] in Schedule.columns, 'Unknown column name'

        columns = ', '.join(list(map(lambda x: x[0], args)))
        values = list(map(lambda x: x[1], args))
        query = 'INSERT INTO schedule (' + columns + ') VALUES (' + ('%s, ' * len(args))[:-2:] + ') RETURNING schedule_id;'
        session.db_execute(query, *values)

        id = session.cursor.fetchall()[0][0]
        return Schedule(session, id)
