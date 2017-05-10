from session import Session
from entry_teacher import Teacher
from entry_class import Class
from entry_subject import Subject
from entry_student import Student
from entry_schedule import Schedule
from entry_mark import Mark

def main():
    session = Session()

    new_student = Student.add(session, (Student.name_first, 'Никита'), (Student.name_last, 'Геевич'), (Student.class_id, 90))
    session.connection.commit()
    print(new_student.id)

if __name__ == "__main__":
    main()
