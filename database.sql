-- =========================================================
-- PARENT TEACHER BRIDGE DATABASE
-- UPDATED MASTER DATABASE SCRIPT
-- =========================================================

CREATE DATABASE IF NOT EXISTS parent_teacher_bridge;

USE parent_teacher_bridge;


-- =========================================================
-- TEACHERS TABLE
-- =========================================================

CREATE TABLE IF NOT EXISTS teachers (

    teacher_id INT AUTO_INCREMENT PRIMARY KEY,

    full_name VARCHAR(100) NOT NULL,

    username VARCHAR(50) NOT NULL UNIQUE,

    password VARCHAR(255) NOT NULL,

    class_assigned VARCHAR(20)

);


-- =========================================================
-- PARENTS TABLE
-- =========================================================

CREATE TABLE IF NOT EXISTS parents (

    parent_id INT AUTO_INCREMENT PRIMARY KEY,

    full_name VARCHAR(100) NOT NULL,

    phone_number VARCHAR(15) NOT NULL UNIQUE,

    password VARCHAR(255) NOT NULL,

    preferred_language VARCHAR(20)

);


-- =========================================================
-- STUDENTS TABLE
-- =========================================================

CREATE TABLE IF NOT EXISTS students (

    student_id INT AUTO_INCREMENT PRIMARY KEY,

    student_name VARCHAR(100) NOT NULL,

    roll_number INT NOT NULL,

    class VARCHAR(20),

    parent_id INT,

    FOREIGN KEY (parent_id)
        REFERENCES parents(parent_id)

);


-- =========================================================
-- ADMINS TABLE
-- =========================================================

CREATE TABLE IF NOT EXISTS admins (

    admin_id INT AUTO_INCREMENT PRIMARY KEY,

    username VARCHAR(50) UNIQUE NOT NULL,

    password VARCHAR(255) NOT NULL

);


-- =========================================================
-- ATTENDANCE TABLE
-- =========================================================

CREATE TABLE IF NOT EXISTS attendance (

    attendance_id INT AUTO_INCREMENT PRIMARY KEY,

    student_id INT,

    attendance_date DATE,

    status VARCHAR(20),

    FOREIGN KEY (student_id)
        REFERENCES students(student_id)

);


-- =========================================================
-- MARKS TABLE
-- =========================================================

CREATE TABLE IF NOT EXISTS marks (

    marks_id INT AUTO_INCREMENT PRIMARY KEY,

    student_id INT,

    subject VARCHAR(50),

    marks_obtained INT,

    FOREIGN KEY (student_id)
        REFERENCES students(student_id)

);


-- =========================================================
-- SCHEMES TABLE
-- =========================================================

CREATE TABLE IF NOT EXISTS schemes (

    scheme_id INT AUTO_INCREMENT PRIMARY KEY,

    scheme_name VARCHAR(100),

    eligible_class VARCHAR(20),

    deadline DATE,

    documents_required VARCHAR(255)

);


-- =========================================================
-- MESSAGES TABLE
-- =========================================================

CREATE TABLE IF NOT EXISTS messages (

    message_id INT AUTO_INCREMENT PRIMARY KEY,

    parent_id INT NOT NULL,

    teacher_id INT NOT NULL,

    sender_role VARCHAR(20) NOT NULL,

    message_type VARCHAR(20)
        NOT NULL DEFAULT 'text',

    message_text TEXT NULL,

    audio_path VARCHAR(500) NULL,

    is_read TINYINT(1)
        NOT NULL DEFAULT 0,

    created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP

);


-- =========================================================
-- ADMIN ACCOUNT
-- =========================================================

INSERT INTO admins (
    username,
    password
)
VALUES (
    'admin',
    'admin123'
)
ON DUPLICATE KEY UPDATE
    password = VALUES(password);


-- =========================================================
-- TEACHER DATA
-- ALL CURRENT TEACHERS -> CLASS 10th
-- =========================================================

UPDATE teachers
SET class_assigned = '10th';


-- ---------------------------------------------------------
-- TEACHER 1
-- ---------------------------------------------------------

INSERT INTO teachers (
    full_name,
    username,
    password,
    class_assigned
)
VALUES (
    'Mrs. Priya Sharma',
    'teacher1',
    '1234',
    '10th'
)
ON DUPLICATE KEY UPDATE

    full_name = VALUES(full_name),

    password = VALUES(password),

    class_assigned = VALUES(class_assigned);


-- ---------------------------------------------------------
-- TEACHER 2
-- ---------------------------------------------------------

INSERT INTO teachers (
    full_name,
    username,
    password,
    class_assigned
)
VALUES (
    'Mr. Rakesh Kumar',
    'teacher2',
    '1234',
    '10th'
)
ON DUPLICATE KEY UPDATE

    full_name = VALUES(full_name),

    password = VALUES(password),

    class_assigned = VALUES(class_assigned);


-- ---------------------------------------------------------
-- TEACHER 3
-- ---------------------------------------------------------

INSERT INTO teachers (
    full_name,
    username,
    password,
    class_assigned
)
VALUES (
    'Ms. Neha Singh',
    'teacher3',
    '1234',
    '10th'
)
ON DUPLICATE KEY UPDATE

    full_name = VALUES(full_name),

    password = VALUES(password),

    class_assigned = VALUES(class_assigned);


-- =========================================================
-- PARENT DATA
-- =========================================================


-- ---------------------------------------------------------
-- EXISTING PARENT 1
-- ---------------------------------------------------------

UPDATE parents
SET
    full_name = 'Suresh Kumar',
    phone_number = '9876543210',
    password = '1234',
    preferred_language = 'English'
WHERE parent_id = 1;


-- ---------------------------------------------------------
-- EXISTING PARENT 2
-- ---------------------------------------------------------

UPDATE parents
SET
    full_name = 'Manas Das',
    phone_number = '9123456780',
    password = '1234',
    preferred_language = 'Odia'
WHERE parent_id = 2;


-- ---------------------------------------------------------
-- EXISTING PARENT 6
-- ---------------------------------------------------------

UPDATE parents
SET
    full_name = 'Rajesh Singh',
    phone_number = '9000000006',
    password = '1234',
    preferred_language = 'English'
WHERE parent_id = 6;


-- ---------------------------------------------------------
-- EXISTING PARENT 7
-- ---------------------------------------------------------

UPDATE parents
SET
    full_name = 'Mahesh Patel',
    phone_number = '9000000007',
    password = '1234',
    preferred_language = 'Hindi'
WHERE parent_id = 7;


-- ---------------------------------------------------------
-- PARENT 3
-- ---------------------------------------------------------

INSERT INTO parents (
    full_name,
    phone_number,
    password,
    preferred_language
)
SELECT
    'Pradip Behera',
    '9000000003',
    '1234',
    'English'
WHERE NOT EXISTS (
    SELECT 1
    FROM parents
    WHERE phone_number = '9000000003'
);


-- ---------------------------------------------------------
-- PARENT 4
-- ---------------------------------------------------------

INSERT INTO parents (
    full_name,
    phone_number,
    password,
    preferred_language
)
SELECT
    'Amit Sharma',
    '9000000004',
    '1234',
    'Hindi'
WHERE NOT EXISTS (
    SELECT 1
    FROM parents
    WHERE phone_number = '9000000004'
);


-- ---------------------------------------------------------
-- PARENT 5
-- ---------------------------------------------------------

INSERT INTO parents (
    full_name,
    phone_number,
    password,
    preferred_language
)
SELECT
    'Sanjay Mishra',
    '9000000005',
    '1234',
    'English'
WHERE NOT EXISTS (
    SELECT 1
    FROM parents
    WHERE phone_number = '9000000005'
);


-- ---------------------------------------------------------
-- PARENT 8
-- ---------------------------------------------------------

INSERT INTO parents (
    full_name,
    phone_number,
    password,
    preferred_language
)
SELECT
    'Ramesh Sahu',
    '9000000008',
    '1234',
    'Odia'
WHERE NOT EXISTS (
    SELECT 1
    FROM parents
    WHERE phone_number = '9000000008'
);


-- ---------------------------------------------------------
-- PARENT 9
-- ---------------------------------------------------------

INSERT INTO parents (
    full_name,
    phone_number,
    password,
    preferred_language
)
SELECT
    'Dinesh Kumar',
    '9000000009',
    '1234',
    'English'
WHERE NOT EXISTS (
    SELECT 1
    FROM parents
    WHERE phone_number = '9000000009'
);


-- ---------------------------------------------------------
-- PARENT 10
-- ---------------------------------------------------------

INSERT INTO parents (
    full_name,
    phone_number,
    password,
    preferred_language
)
SELECT
    'Sunita Verma',
    '9000000010',
    '1234',
    'Hindi'
WHERE NOT EXISTS (
    SELECT 1
    FROM parents
    WHERE phone_number = '9000000010'
);


-- =========================================================
-- FORCE ALL EXISTING STUDENTS TO CLASS 10th
-- =========================================================

UPDATE students
SET class = '10th';


-- =========================================================
-- STUDENT ROLL 1
-- RAHUL KUMAR
-- =========================================================

UPDATE students
SET
    student_name = 'Rahul Kumar',
    class = '10th',
    parent_id = (
        SELECT parent_id
        FROM parents
        WHERE phone_number = '9876543210'
        LIMIT 1
    )
WHERE roll_number = 1
LIMIT 1;


-- =========================================================
-- STUDENT ROLL 2
-- ANITA DAS
-- =========================================================

UPDATE students
SET
    student_name = 'Anita Das',
    class = '10th',
    parent_id = (
        SELECT parent_id
        FROM parents
        WHERE phone_number = '9123456780'
        LIMIT 1
    )
WHERE roll_number = 2
LIMIT 1;


-- =========================================================
-- STUDENT ROLL 3
-- RIYA SINGH
-- =========================================================

UPDATE students
SET
    student_name = 'Riya Singh',
    class = '10th',
    parent_id = (
        SELECT parent_id
        FROM parents
        WHERE phone_number = '9000000006'
        LIMIT 1
    )
WHERE roll_number = 3
LIMIT 1;


-- =========================================================
-- STUDENT ROLL 4
-- SNEHA PATEL
-- =========================================================

UPDATE students
SET
    student_name = 'Sneha Patel',
    class = '10th',
    parent_id = (
        SELECT parent_id
        FROM parents
        WHERE phone_number = '9000000007'
        LIMIT 1
    )
WHERE roll_number = 4
LIMIT 1;


-- =========================================================
-- STUDENT ROLL 5
-- ARJUN BEHERA
-- =========================================================

INSERT INTO students (
    student_name,
    roll_number,
    class,
    parent_id
)
SELECT
    'Arjun Behera',
    5,
    '10th',
    (
        SELECT parent_id
        FROM parents
        WHERE phone_number = '9000000003'
        LIMIT 1
    )
WHERE NOT EXISTS (
    SELECT 1
    FROM students
    WHERE roll_number = 5
);


-- =========================================================
-- STUDENT ROLL 6
-- KAVYA SHARMA
-- =========================================================

INSERT INTO students (
    student_name,
    roll_number,
    class,
    parent_id
)
SELECT
    'Kavya Sharma',
    6,
    '10th',
    (
        SELECT parent_id
        FROM parents
        WHERE phone_number = '9000000004'
        LIMIT 1
    )
WHERE NOT EXISTS (
    SELECT 1
    FROM students
    WHERE roll_number = 6
);


-- =========================================================
-- STUDENT ROLL 7
-- ADITYA MISHRA
-- =========================================================

INSERT INTO students (
    student_name,
    roll_number,
    class,
    parent_id
)
SELECT
    'Aditya Mishra',
    7,
    '10th',
    (
        SELECT parent_id
        FROM parents
        WHERE phone_number = '9000000005'
        LIMIT 1
    )
WHERE NOT EXISTS (
    SELECT 1
    FROM students
    WHERE roll_number = 7
);


-- =========================================================
-- STUDENT ROLL 8
-- POOJA SAHU
-- =========================================================

INSERT INTO students (
    student_name,
    roll_number,
    class,
    parent_id
)
SELECT
    'Pooja Sahu',
    8,
    '10th',
    (
        SELECT parent_id
        FROM parents
        WHERE phone_number = '9000000008'
        LIMIT 1
    )
WHERE NOT EXISTS (
    SELECT 1
    FROM students
    WHERE roll_number = 8
);


-- =========================================================
-- STUDENT ROLL 9
-- AYUSH KUMAR
-- =========================================================

INSERT INTO students (
    student_name,
    roll_number,
    class,
    parent_id
)
SELECT
    'Ayush Kumar',
    9,
    '10th',
    (
        SELECT parent_id
        FROM parents
        WHERE phone_number = '9000000009'
        LIMIT 1
    )
WHERE NOT EXISTS (
    SELECT 1
    FROM students
    WHERE roll_number = 9
);


-- =========================================================
-- STUDENT ROLL 10
-- NEHA VERMA
-- =========================================================

INSERT INTO students (
    student_name,
    roll_number,
    class,
    parent_id
)
SELECT
    'Neha Verma',
    10,
    '10th',
    (
        SELECT parent_id
        FROM parents
        WHERE phone_number = '9000000010'
        LIMIT 1
    )
WHERE NOT EXISTS (
    SELECT 1
    FROM students
    WHERE roll_number = 10
);


-- =========================================================
-- FIX EXISTING PLACEHOLDER NAMES IF PRESENT
-- =========================================================

UPDATE students
SET student_name = 'Arjun Behera'
WHERE student_name = 'Student 5'
LIMIT 1;


UPDATE students
SET student_name = 'Kavya Sharma'
WHERE student_name = 'Student 6'
LIMIT 1;


UPDATE parents
SET full_name = 'Suresh Kumar'
WHERE full_name = 'Parent 1'
LIMIT 1;


UPDATE parents
SET full_name = 'Manas Das'
WHERE full_name = 'Parent 2'
LIMIT 1;


-- =========================================================
-- GOVERNMENT SCHEMES
-- ALL CURRENT SCHEME CLASS VALUES -> 10th
-- =========================================================

UPDATE schemes
SET eligible_class = '10th';


-- ---------------------------------------------------------
-- SAMPLE SCHEME 1
-- ---------------------------------------------------------

INSERT INTO schemes (
    scheme_name,
    eligible_class,
    deadline,
    documents_required
)
SELECT
    'Scholarship Scheme',
    '10th',
    '2026-03-31',
    'Aadhaar, Income Certificate'
WHERE NOT EXISTS (
    SELECT 1
    FROM schemes
    WHERE scheme_name = 'Scholarship Scheme'
);


-- ---------------------------------------------------------
-- SAMPLE SCHEME 2
-- ---------------------------------------------------------

INSERT INTO schemes (
    scheme_name,
    eligible_class,
    deadline,
    documents_required
)
SELECT
    'Mid-Day Meal Benefit',
    '10th',
    '2026-12-31',
    'School ID'
WHERE NOT EXISTS (
    SELECT 1
    FROM schemes
    WHERE scheme_name = 'Mid-Day Meal Benefit'
);


-- =========================================================
-- VERIFICATION QUERIES
-- RUN THESE AFTER THE UPDATE
-- =========================================================


-- Check all students and corresponding parents

SELECT
    s.student_id,
    s.student_name,
    s.roll_number,
    s.class,
    s.parent_id,
    p.full_name AS parent_name,
    p.phone_number
FROM students s
LEFT JOIN parents p
    ON s.parent_id = p.parent_id
ORDER BY
    s.roll_number;


-- Check teachers

SELECT
    teacher_id,
    full_name,
    username,
    class_assigned
FROM teachers
ORDER BY teacher_id;


-- Check Class 10 students only

SELECT
    student_id,
    student_name,
    roll_number,
    class,
    parent_id
FROM students
WHERE TRIM(class) = '10th'
ORDER BY roll_number;