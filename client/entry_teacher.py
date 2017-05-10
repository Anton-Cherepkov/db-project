class Teacher:
    teacher_id = 'teacher_id'
    name_first = 'name_first'
    name_middle = 'name_middle'
    name_last = 'name_last'
    phone = 'phone'
    columns = [name_first, name_middle, name_last, phone]

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

    @staticmethod
    def add(session, *args):  # usage: add((Student.name_first, 'Антон'), (Student.name_middle, 'Юрьевич'))
        for arg in args:
            assert arg[0] in Teacher.columns, 'Unknown column name'

        columns = ', '.join(list(map(lambda x: x[0], args)))
        values = list(map(lambda x: x[1], args))
        query = 'INSERT INTO teachers (' + columns + ') VALUES (' + ('%s, ' * len(args))[:-2:] + ') RETURNING teacher_id;'
        session.db_execute(query, *values)

        id = session.cursor.fetchall()[0][0]
        return Teacher(session, id)
