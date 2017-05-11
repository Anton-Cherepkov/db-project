from session import Session, Role

from entry_teacher import Teacher
from entry_class import Class
from entry_subject import Subject
from entry_student import Student
from entry_schedule import Schedule
from entry_mark import Mark

import menu_admin


def main():
    session = Session()

    if session.user_role is Role.ADMINISTRATOR:
        menu_admin.menu_admin(session)

if __name__ == "__main__":
    main()
