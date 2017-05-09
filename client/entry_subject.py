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
