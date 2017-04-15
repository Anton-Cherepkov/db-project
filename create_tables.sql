CREATE TABLE teachers (
  teacher_id  SERIAL PRIMARY KEY,
  name_first  VARCHAR(100) NOT NULL,
  name_middle VARCHAR(100),
  name_last   VARCHAR(100) NOT NULL,
  phone       VARCHAR(30)
);

CREATE TABLE classes (
  class_number  INTEGER,
  class_letter  CHAR(1),
  teacher_id    INTEGER NOT NULL REFERENCES teachers (teacher_id),
  PRIMARY KEY   (class_number, class_letter)
);

CREATE TABLE subjects (
  subject_id  SERIAL PRIMARY KEY,
  name        VARCHAR(100) NOT NULL
);

CREATE TABLE subjects_teachers (
  subject_id INTEGER NOT NULL REFERENCES subjects (subject_id),
  teacher_id INTEGER NOT NULL REFERENCES teachers (teacher_id),
  CONSTRAINT st UNIQUE (subject_id, teacher_id)
);

CREATE TABLE students (
  student_id    SERIAL PRIMARY KEY,
  name_first    VARCHAR(100) NOT NULL,
  name_middle   VARCHAR(100),
  name_last     VARCHAR(100) NOT NULL,
  class_number  INTEGER NOT NULL,
  class_letter  CHAR(1) NOT NULL,
  phone         VARCHAR(30),
  FOREIGN KEY (class_number, class_letter) REFERENCES classes (class_number, class_letter)
);

CREATE TABLE schedule (
  schedule_id   SERIAL PRIMARY KEY,
  subject_id    INTEGER NOT NULL REFERENCES subjects (subject_id),
  class_number  INTEGER NOT NULL,
  class_letter  CHAR(1) NOT NULL,
  teacher_id    INTEGER NOT NULL REFERENCES teachers (teacher_id),
  day           SMALLINT NOT NULL CHECK (day >= 0 AND day <= 6), -- 0(Sunday), ... 6(Saturday)
  time_begin    TIME NOT NULL,
  time_duration INTERVAL NOT NULL,
  FOREIGN KEY (class_number, class_letter) REFERENCES classes (class_number, class_letter)
);

CREATE TABLE marks (
  mark_id     SERIAL PRIMARY KEY,
  value       SMALLINT NOT NULL CHECK (value >= 0),
  teacher_id  INTEGER NOT NULL REFERENCES teachers (teacher_id),
  student_id  INTEGER NOT NULL REFERENCES students (student_id),
  subject_id  INTEGER NOT NULL REFERENCES subjects (subject_id),
  time        TIMESTAMP
);

CREATE TABLE users_teachers (
  user_id     SERIAL PRIMARY KEY,
  login       VARCHAR(30) UNIQUE NOT NULL,
  password    VARCHAR(32) NOT NULL, -- md5 hash
  teacher_id  INTEGER NOT NULL REFERENCES teachers (teacher_id)
);

CREATE TABLE users_students (
  user_id     SERIAL PRIMARY KEY,
  login       VARCHAR(30) UNIQUE NOT NULL,
  password    VARCHAR(32) NOT NULL, -- md5 hash
  student_id  INTEGER NOT NULL REFERENCES students (student_id)
);
