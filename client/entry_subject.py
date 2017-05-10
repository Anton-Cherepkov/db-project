class Subject:
    subject_id = 'subject_id'
    name = 'name'
    columns = [name]

    def __init__(self, session, id):
        self.session = session
        self.id = id

    def get(self, column):
        assert column in Subject.columns, 'Unknown column name'

        self.session.db_execute('SELECT ' + column + ' FROM subjects WHERE subject_id = %s;', self.id)
        return self.session.cursor.fetchall()[0][0]

    def set(self, column, value):
        assert column in Subject.columns, 'Unknown column name'

        self.session.db_execute('UPDATE subjects SET ' + column + ' = %s WHERE subject_id = %s;', value, self.id)

    @staticmethod
    def add(session, *args):  # usage: add((Student.name_first, 'Антон'), (Student.name_middle, 'Юрьевич'))
        for arg in args:
            assert arg[0] in Subject.columns, 'Unknown column name'

        columns = ', '.join(list(map(lambda x: x[0], args)))
        values = list(map(lambda x: x[1], args))
        query = 'INSERT INTO subjects (' + columns + ') VALUES (' + ('%s, ' * len(args))[:-2:] + ') RETURNING subject_id;'
        session.db_execute(query, *values)

        id = session.cursor.fetchall()[0][0]
        return Subject(session, id)