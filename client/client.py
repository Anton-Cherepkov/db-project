from session import Session
from entry_teacher import Teacher
from entry_class import Class
from entry_subject import Subject
from entry_student import Student
from entry_schedule import Schedule
from entry_mark import Mark

def main():
    session = Session()

    subject = Subject(session, 107)
    print(subject.get(Subject.name))
    subject.set(Subject.name, 'Русский язык')
    session.connection.commit()
    print(subject.get(Subject.name))

if __name__ == "__main__":
    main()
