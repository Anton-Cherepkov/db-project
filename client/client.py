from session import Session, Role

from entry_teacher import Teacher
from entry_class import Class
from entry_subject import Subject
from entry_student import Student
from entry_schedule import Schedule
from entry_mark import Mark

import menu_admin
import menu_student
import menu_teacher


def main():
    session = Session()

    if session.user_role is Role.ADMINISTRATOR:
        menu_admin.menu_admin(session)
    elif session.user_role is Role.TEACHER:
        interactor = menu_teacher.TeacherInteract(session)
        interactor.handler_menu_teacher()
    elif session.user_role is Role.STUDENT:
        menu_student.menu_student(session)

if __name__ == "__main__":
    main()
