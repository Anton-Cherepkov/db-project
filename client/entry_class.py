class Class:
    class_id = 'class_id'
    class_number = 'class_number'
    class_letter = 'class_letter'
    teacher_id = 'teacher_id'
    columns = [class_number, class_letter, teacher_id]

    def __init__(self, session, id):
        self.session = session
        self.id = id

    def get(self, column):
        assert column in Class.columns, 'Unknown column name'

        self.session.db_execute('SELECT ' + column + ' FROM classes WHERE class_id = %s;', self.id)
        return self.session.cursor.fetchall()[0][0]

    def set(self, column, value):
        assert column in Class.columns, 'Unknown column name'

        self.session.db_execute('UPDATE classes SET ' + column + ' = %s WHERE class_id = %s;', value, self.id)

    @staticmethod
    def add(session, *args):  # usage: add((Student.name_first, 'Антон'), (Student.name_middle, 'Юрьевич'))
        for arg in args:
            assert arg[0] in Class.columns, 'Unknown column name'

        columns = ', '.join(list(map(lambda x: x[0], args)))
        values = list(map(lambda x: x[1], args))
        query = 'INSERT INTO classes (' + columns + ') VALUES (' + ('%s, ' * len(args))[:-2:] + ') RETURNING class_id;'
        session.db_execute(query, *values)

        id = session.cursor.fetchall()[0][0]
        return Class(session, id)
