import os
import uuid
from datetime import date

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify
)

import mysql.connector
from werkzeug.utils import secure_filename


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

app.secret_key = "parent_teacher_bridge_secret_key"


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "parent_teacher_bridge"
}


# =========================================================
# PROJECT-WIDE CLASS
# =========================================================

# The project now uses Class 10th as the common class
# for the current student/teacher dataset.
PROJECT_CLASS = "10th"


def get_db_connection():
    """
    Create a fresh MySQL connection whenever a route
    needs to access the database.
    """
    return mysql.connector.connect(**DB_CONFIG)


# =========================================================
# GLOBAL TEMPLATE DATA
# =========================================================

@app.context_processor
def inject_project_data():
    """
    Make the common project class available to every
    Jinja template.

    Templates can use:

        {{ project_class }}
    """
    return {
        "project_class": PROJECT_CLASS
    }


# =========================================================
# VOICE MESSAGE STORAGE
# =========================================================

VOICE_UPLOAD_FOLDER = os.path.join(
    app.static_folder,
    "uploads",
    "voice_messages"
)

os.makedirs(VOICE_UPLOAD_FOLDER, exist_ok=True)


ALLOWED_AUDIO_EXTENSIONS = {
    "webm",
    "wav",
    "mp3",
    "ogg",
    "m4a",
    "mp4"
}


def allowed_audio_file(filename):
    """
    Check whether an uploaded audio filename
    has a supported extension.
    """
    if not filename or "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in ALLOWED_AUDIO_EXTENSIONS


# =========================================================
# DATABASE HELPERS
# =========================================================

def get_all_students():
    """
    Return all students from the database.

    Parent information is also loaded so the same
    student-parent relationship can be used throughout
    the project.
    """
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                s.student_id,
                s.student_name,
                s.roll_number,
                s.class,
                s.parent_id,
                p.full_name AS parent_name
            FROM students s
            LEFT JOIN parents p
                ON s.parent_id = p.parent_id
            ORDER BY s.roll_number, s.student_name
            """
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        db.close()


def get_students_for_current_user():
    """
    Return students according to the logged-in role.

    Teacher:
        Students belonging to the teacher's assigned class.

    Parent:
        Only students linked to that parent.

    Admin:
        All students.

    If no role is available, all students are returned
    so the existing pages remain usable during testing.
    """

    role = session.get("role")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        # -------------------------------------------------
        # TEACHER
        # -------------------------------------------------

        if role == "teacher" and session.get("teacher_id"):

            teacher_class = str(
                session.get("teacher_class") or ""
            ).strip()

            # Newly created teachers without an assigned
            # class are treated as Class 10th for this
            # project dataset.
            if not teacher_class:
                teacher_class = PROJECT_CLASS

            cursor.execute(
                """
                SELECT
                    s.student_id,
                    s.student_name,
                    s.roll_number,
                    s.class,
                    s.parent_id,
                    p.full_name AS parent_name
                FROM students s
                LEFT JOIN parents p
                    ON s.parent_id = p.parent_id
                WHERE TRIM(s.class) = TRIM(%s)
                ORDER BY s.roll_number, s.student_name
                """,
                (teacher_class,)
            )

            return cursor.fetchall()

        # -------------------------------------------------
        # PARENT
        # -------------------------------------------------

        if role == "parent" and session.get("parent_id"):

            cursor.execute(
                """
                SELECT
                    s.student_id,
                    s.student_name,
                    s.roll_number,
                    s.class,
                    s.parent_id,
                    p.full_name AS parent_name
                FROM students s
                LEFT JOIN parents p
                    ON s.parent_id = p.parent_id
                WHERE s.parent_id = %s
                ORDER BY s.student_id
                """,
                (session.get("parent_id"),)
            )

            return cursor.fetchall()

        # -------------------------------------------------
        # ADMIN / TESTING
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                s.student_id,
                s.student_name,
                s.roll_number,
                s.class,
                s.parent_id,
                p.full_name AS parent_name
            FROM students s
            LEFT JOIN parents p
                ON s.parent_id = p.parent_id
            ORDER BY s.roll_number, s.student_name
            """
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        db.close()


def get_parent_student(parent_id):
    """
    Return the first student linked to the parent.
    """

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                student_id,
                student_name,
                roll_number,
                class,
                parent_id
            FROM students
            WHERE parent_id = %s
            ORDER BY student_id
            LIMIT 1
            """,
            (parent_id,)
        )

        return cursor.fetchone()

    finally:

        cursor.close()
        db.close()


def get_parent_teacher(parent_id):
    """
    Find the teacher assigned to the class of the
    parent's linked child.

    Returns:
        (student, teacher)
    """

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                s.student_id,
                s.student_name,
                s.roll_number,
                s.class,
                s.parent_id,

                t.teacher_id,
                t.full_name AS teacher_full_name,
                t.username AS teacher_username,
                t.class_assigned

            FROM students s

            LEFT JOIN teachers t
                ON TRIM(s.class) = TRIM(t.class_assigned)

            WHERE s.parent_id = %s

            ORDER BY
                CASE
                    WHEN t.teacher_id IS NULL THEN 1
                    ELSE 0
                END,
                t.teacher_id

            LIMIT 1
            """,
            (parent_id,)
        )

        row = cursor.fetchone()

        if not row:
            return None, None

        student = {
            "student_id": row["student_id"],
            "student_name": row["student_name"],
            "roll_number": row["roll_number"],
            "class": row["class"],
            "parent_id": row["parent_id"]
        }

        teacher = None

        if row["teacher_id"] is not None:

            teacher = {
                "teacher_id": row["teacher_id"],
                "full_name": row["teacher_full_name"],
                "username": row["teacher_username"],
                "class_assigned": row["class_assigned"]
            }

        return student, teacher

    finally:

        cursor.close()
        db.close()


# =========================================================
# TEACHER DASHBOARD HELPERS
# =========================================================

def get_grade_from_average(average):
    """
    Convert an average mark into a simple display grade.

    This is used only by the Teacher Dashboard display.
    """

    if average is None:
        return "-"

    try:
        average = float(average)
    except (TypeError, ValueError):
        return "-"

    if average >= 90:
        return "A+"

    if average >= 80:
        return "A"

    if average >= 70:
        return "B+"

    if average >= 60:
        return "B"

    if average >= 50:
        return "C"

    return "D"


def get_teacher_dashboard_data(teacher_id):
    """
    Load dynamic Teacher Dashboard information from MySQL.

    This removes the old hard-coded sample students
    and makes the dashboard use the same database data
    as Admin, Attendance, Marks and Parent pages.
    """

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        # -------------------------------------------------
        # TEACHER
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                teacher_id,
                full_name,
                username,
                class_assigned
            FROM teachers
            WHERE teacher_id = %s
            """,
            (teacher_id,)
        )

        teacher = cursor.fetchone()

        if not teacher:
            return {
                "teacher": None,
                "teacher_class": PROJECT_CLASS,
                "teacher_students": [],
                "total_students": 0,
                "present_today": 0,
                "absent_today": 0,
                "attendance_rate": 0,
                "class_performance": 0,
                "top_student": None,
                "students_needing_support": 0
            }

        teacher_class = str(
            teacher.get("class_assigned") or PROJECT_CLASS
        ).strip()

        if not teacher_class:
            teacher_class = PROJECT_CLASS

        # -------------------------------------------------
        # STUDENTS + PARENTS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                s.student_id,
                s.student_name,
                s.roll_number,
                s.class,
                s.parent_id,
                p.full_name AS parent_name

            FROM students s

            LEFT JOIN parents p
                ON s.parent_id = p.parent_id

            WHERE TRIM(s.class) = TRIM(%s)

            ORDER BY
                s.roll_number,
                s.student_name
            """,
            (teacher_class,)
        )

        teacher_students = cursor.fetchall()

        total_students = len(teacher_students)

        student_ids = [
            student["student_id"]
            for student in teacher_students
        ]

        # -------------------------------------------------
        # DEFAULT VALUES
        # -------------------------------------------------

        attendance_by_student = {}
        marks_by_student = {}

        # -------------------------------------------------
        # ATTENDANCE SUMMARY FOR EACH STUDENT
        # -------------------------------------------------

        if student_ids:

            placeholders = ",".join(
                ["%s"] * len(student_ids)
            )

            attendance_query = f"""
                SELECT
                    student_id,

                    COUNT(*) AS total_days,

                    SUM(
                        CASE
                            WHEN LOWER(TRIM(status)) = 'present'
                            THEN 1
                            ELSE 0
                        END
                    ) AS present_days

                FROM attendance

                WHERE student_id IN ({placeholders})

                GROUP BY student_id
            """

            cursor.execute(
                attendance_query,
                student_ids
            )

            attendance_rows = cursor.fetchall()

            for row in attendance_rows:

                total_days = int(
                    row.get("total_days") or 0
                )

                present_days = int(
                    row.get("present_days") or 0
                )

                if total_days > 0:

                    percentage = round(
                        (
                            present_days /
                            total_days
                        ) * 100,
                        1
                    )

                else:

                    percentage = 0

                attendance_by_student[
                    row["student_id"]
                ] = percentage

        # -------------------------------------------------
        # MARKS SUMMARY FOR EACH STUDENT
        # -------------------------------------------------

        if student_ids:

            placeholders = ",".join(
                ["%s"] * len(student_ids)
            )

            marks_query = f"""
                SELECT
                    student_id,
                    AVG(marks_obtained) AS average_marks
                FROM marks
                WHERE student_id IN ({placeholders})
                GROUP BY student_id
            """

            cursor.execute(
                marks_query,
                student_ids
            )

            marks_rows = cursor.fetchall()

            for row in marks_rows:

                try:

                    average = float(
                        row["average_marks"]
                    )

                except (
                    TypeError,
                    ValueError
                ):

                    average = None

                marks_by_student[
                    row["student_id"]
                ] = average

        # -------------------------------------------------
        # ADD CALCULATED INFORMATION TO STUDENTS
        # -------------------------------------------------

        for student in teacher_students:

            student_id = student["student_id"]

            attendance_percentage = (
                attendance_by_student.get(
                    student_id,
                    0
                )
            )

            average_marks = marks_by_student.get(
                student_id
            )

            student["attendance_percentage"] = (
                attendance_percentage
            )

            student["average_marks"] = (
                average_marks
            )

            student["grade"] = (
                get_grade_from_average(
                    average_marks
                )
            )

        # -------------------------------------------------
        # TODAY'S ATTENDANCE
        # -------------------------------------------------

        present_today = 0
        absent_today = 0

        if student_ids:

            placeholders = ",".join(
                ["%s"] * len(student_ids)
            )

            cursor.execute(
                f"""
                SELECT
                    LOWER(TRIM(status)) AS status,
                    COUNT(*) AS total
                FROM attendance
                WHERE attendance_date = %s
                AND student_id IN ({placeholders})
                GROUP BY LOWER(TRIM(status))
                """,
                [date.today().isoformat()] + student_ids
            )

            today_rows = cursor.fetchall()

            for row in today_rows:

                status = row["status"]
                count = int(
                    row["total"] or 0
                )

                if status == "present":
                    present_today += count

                elif status == "absent":
                    absent_today += count

        # -------------------------------------------------
        # ATTENDANCE RATE
        # -------------------------------------------------

        if total_students > 0:

            attendance_rate = round(
                (
                    present_today /
                    total_students
                ) * 100,
                1
            )

        else:

            attendance_rate = 0

        # -------------------------------------------------
        # CLASS PERFORMANCE
        # -------------------------------------------------

        students_with_marks = [
            student["average_marks"]
            for student in teacher_students
            if student["average_marks"] is not None
        ]

        if students_with_marks:

            class_performance = round(
                sum(students_with_marks)
                / len(students_with_marks),
                1
            )

        else:

            class_performance = 0

        # -------------------------------------------------
        # TOP STUDENT
        # -------------------------------------------------

        marked_students = [
            student
            for student in teacher_students
            if student["average_marks"] is not None
        ]

        if marked_students:

            top_student = max(
                marked_students,
                key=lambda student:
                    float(student["average_marks"])
            )

        else:

            top_student = None

        # -------------------------------------------------
        # STUDENTS NEEDING SUPPORT
        # -------------------------------------------------

        students_needing_support = sum(
            1
            for student in teacher_students
            if (
                student["average_marks"] is not None
                and float(student["average_marks"]) < 50
            )
        )

        return {
            "teacher": teacher,

            "teacher_class": (
                teacher_class
            ),

            "teacher_students": (
                teacher_students
            ),

            "total_students": (
                total_students
            ),

            "present_today": (
                present_today
            ),

            "absent_today": (
                absent_today
            ),

            "attendance_rate": (
                attendance_rate
            ),

            "class_performance": (
                class_performance
            ),

            "top_student": (
                top_student
            ),

            "students_needing_support": (
                students_needing_support
            )
        }

    finally:

        cursor.close()
        db.close()


# =========================================================
# PARENT DASHBOARD DATA
# =========================================================

def get_parent_dashboard_data(parent_id):
    """
    Load all data expected by parent_dashboard.html.
    """

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        # -------------------------------------------------
        # PARENT
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                parent_id,
                full_name,
                phone_number,
                preferred_language
            FROM parents
            WHERE parent_id = %s
            """,
            (parent_id,)
        )

        parent = cursor.fetchone()

        # -------------------------------------------------
        # LINKED STUDENT
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                student_id,
                student_name,
                roll_number,
                class,
                parent_id
            FROM students
            WHERE parent_id = %s
            ORDER BY student_id
            LIMIT 1
            """,
            (parent_id,)
        )

        student = cursor.fetchone()

        attendance_records = []
        marks_records = []

        total_attendance_days = 0
        present_days = 0
        absent_days = 0
        attendance_percentage = 0

        total_marks = 0
        average_marks = 0
        marks_percentage = 0

        # -------------------------------------------------
        # ATTENDANCE
        # -------------------------------------------------

        if student:

            cursor.execute(
                """
                SELECT
                    attendance_date,
                    status
                FROM attendance
                WHERE student_id = %s
                ORDER BY attendance_date DESC, attendance_id DESC
                """,
                (student["student_id"],)
            )

            attendance_records = cursor.fetchall()

            total_attendance_days = len(
                attendance_records
            )

            for record in attendance_records:

                status = str(
                    record.get("status", "")
                ).strip().lower()

                if status == "present":
                    present_days += 1

                elif status == "absent":
                    absent_days += 1

            if total_attendance_days > 0:

                attendance_percentage = round(
                    (
                        present_days /
                        total_attendance_days
                    ) * 100,
                    1
                )

        # -------------------------------------------------
        # MARKS
        # -------------------------------------------------

        if student:

            cursor.execute(
                """
                SELECT
                    subject,
                    marks_obtained
                FROM marks
                WHERE student_id = %s
                ORDER BY subject
                """,
                (student["student_id"],)
            )

            marks_records = cursor.fetchall()

            numeric_marks = []

            for mark in marks_records:

                try:

                    numeric_marks.append(
                        float(
                            mark["marks_obtained"]
                        )
                    )

                except (
                    TypeError,
                    ValueError
                ):
                    pass

            if numeric_marks:

                total_marks = round(
                    sum(numeric_marks),
                    2
                )

                average_marks = round(
                    total_marks /
                    len(numeric_marks),
                    2
                )

                marks_percentage = round(
                    average_marks,
                    2
                )

        # -------------------------------------------------
        # TEACHER CONNECTION
        # -------------------------------------------------

        teacher = None

        if student:

            cursor.execute(
                """
                SELECT
                    teacher_id,
                    full_name,
                    username,
                    class_assigned
                FROM teachers
                WHERE TRIM(class_assigned) = TRIM(%s)
                ORDER BY teacher_id
                LIMIT 1
                """,
                (student["class"],)
            )

            teacher = cursor.fetchone()

        # -------------------------------------------------
        # CURRENT PROJECT UPDATES
        # -------------------------------------------------

        updates = [
            {
                "icon": "📚",
                "title": "Math Homework",
                "text": "Math homework is due tomorrow."
            },
            {
                "icon": "🏫",
                "title": "School Holiday",
                "text": "School will remain closed on Monday."
            },
            {
                "icon": "🎓",
                "title": "Scholarship Application",
                "text": "A new scholarship application is now open."
            },
            {
                "icon": "👥",
                "title": "Parent Teacher Meeting",
                "text": "Check school announcements for the next meeting."
            }
        ]

        return {
            "parent": parent,
            "student": student,

            "attendance_records": (
                attendance_records
            ),

            "total_attendance_days": (
                total_attendance_days
            ),

            "present_days": (
                present_days
            ),

            "absent_days": (
                absent_days
            ),

            "attendance_percentage": (
                attendance_percentage
            ),

            "marks_records": (
                marks_records
            ),

            "total_marks": (
                total_marks
            ),

            "average_marks": (
                average_marks
            ),

            "marks_percentage": (
                marks_percentage
            ),

            "teacher": teacher,

            "updates": updates,

            "project_class": PROJECT_CLASS
        }

    finally:

        cursor.close()
        db.close()


# =========================================================
# MESSAGE DATABASE
# =========================================================

def ensure_messages_table():
    """
    Create the messages table if it does not exist.
    """

    db = get_db_connection()
    cursor = db.cursor()

    try:

        cursor.execute(
            """
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
            )
            """
        )

        db.commit()

    finally:

        cursor.close()
        db.close()


# =========================================================
# MESSAGE SERIALIZATION
# =========================================================

def serialize_message(message):
    """
    Convert MySQL message data to JSON-safe data.
    """

    return {
        "message_id": message.get("message_id"),
        "parent_id": message.get("parent_id"),
        "teacher_id": message.get("teacher_id"),
        "sender_role": message.get("sender_role"),
        "message_type": message.get("message_type"),
        "message_text": message.get("message_text"),
        "audio_path": message.get("audio_path"),

        "audio_url": (
            url_for(
                "static",
                filename=message["audio_path"]
            )
            if message.get("audio_path")
            else None
        ),

        "is_read": message.get("is_read"),

        "created_at": (
            message["created_at"].isoformat()
            if message.get("created_at")
            else None
        )
    }


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        role = request.form.get(
            "role",
            ""
        ).strip().lower()

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if not role or not username or not password:

            flash(
                "Please enter all login details."
            )

            return redirect(
                url_for("login")
            )

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        try:

            session.clear()

            # -------------------------------------------------
            # ADMIN LOGIN
            # -------------------------------------------------

            if role == "admin":

                cursor.execute(
                    """
                    SELECT
                        admin_id,
                        username
                    FROM admins
                    WHERE username = %s
                    AND password = %s
                    """,
                    (
                        username,
                        password
                    )
                )

                admin = cursor.fetchone()

                if admin:

                    session["admin_id"] = (
                        admin["admin_id"]
                    )

                    session["admin_username"] = (
                        admin["username"]
                    )

                    session["role"] = "admin"

                    return redirect(
                        url_for(
                            "admin_dashboard"
                        )
                    )

                flash(
                    "Invalid admin username or password."
                )

                return redirect(
                    url_for("login")
                )

            # -------------------------------------------------
            # TEACHER LOGIN
            # -------------------------------------------------

            elif role == "teacher":

                cursor.execute(
                    """
                    SELECT
                        teacher_id,
                        full_name,
                        username,
                        class_assigned
                    FROM teachers
                    WHERE username = %s
                    AND password = %s
                    """,
                    (
                        username,
                        password
                    )
                )

                teacher = cursor.fetchone()

                if teacher:

                    teacher_class = str(
                        teacher.get(
                            "class_assigned"
                        ) or PROJECT_CLASS
                    ).strip()

                    if not teacher_class:
                        teacher_class = PROJECT_CLASS

                    session["teacher_id"] = (
                        teacher["teacher_id"]
                    )

                    session["teacher_name"] = (
                        teacher["full_name"]
                    )

                    session["teacher_username"] = (
                        teacher["username"]
                    )

                    session["teacher_class"] = (
                        teacher_class
                    )

                    session["role"] = "teacher"

                    return redirect(
                        url_for(
                            "teacher_dashboard"
                        )
                    )

                flash(
                    "Invalid teacher username or password."
                )

                return redirect(
                    url_for("login")
                )

            # -------------------------------------------------
            # PARENT LOGIN
            # -------------------------------------------------

            elif role == "parent":

                cursor.execute(
                    """
                    SELECT
                        parent_id,
                        full_name,
                        phone_number,
                        preferred_language
                    FROM parents
                    WHERE phone_number = %s
                    AND password = %s
                    """,
                    (
                        username,
                        password
                    )
                )

                parent = cursor.fetchone()

                if parent:

                    session["parent_id"] = (
                        parent["parent_id"]
                    )

                    session["parent_name"] = (
                        parent["full_name"]
                    )

                    session["parent_phone"] = (
                        parent["phone_number"]
                    )

                    session["parent_language"] = (
                        parent["preferred_language"]
                    )

                    session["role"] = "parent"

                    return redirect(
                        url_for(
                            "parent_dashboard"
                        )
                    )

                flash(
                    "Invalid parent phone number or password."
                )

                return redirect(
                    url_for("login")
                )

            else:

                flash(
                    "Invalid role selected."
                )

                return redirect(
                    url_for("login")
                )

        except mysql.connector.Error as error:

            session.clear()

            flash(
                "Database error: " + str(error)
            )

            return redirect(
                url_for("login")
            )

        finally:

            cursor.close()
            db.close()

    return render_template(
        "login.html"
    )


# =========================================================
# SIGN UP
# =========================================================

@app.route(
    "/signup",
    methods=["GET", "POST"]
)
def signup():

    if request.method == "POST":

        full_name = request.form.get(
            "full_name",
            ""
        ).strip()

        contact = request.form.get(
            "contact",
            ""
        ).strip()

        role = request.form.get(
            "role",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        if (
            not full_name
            or not contact
            or not role
            or not password
        ):

            flash(
                "Please fill in all signup details."
            )

            return redirect(
                url_for("signup")
            )

        db = get_db_connection()
        cursor = db.cursor()

        try:

            # -------------------------------------------------
            # TEACHER
            # -------------------------------------------------

            if role == "teacher":

                cursor.execute(
                    """
                    SELECT teacher_id
                    FROM teachers
                    WHERE username = %s
                    """,
                    (contact,)
                )

                existing = cursor.fetchone()

                if existing:

                    flash(
                        "Teacher account already exists."
                    )

                    return redirect(
                        url_for("signup")
                    )

                cursor.execute(
                    """
                    INSERT INTO teachers
                    (
                        full_name,
                        username,
                        password,
                        class_assigned
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        full_name,
                        contact,
                        password,
                        PROJECT_CLASS
                    )
                )

            # -------------------------------------------------
            # PARENT
            # -------------------------------------------------

            elif role == "parent":

                cursor.execute(
                    """
                    SELECT parent_id
                    FROM parents
                    WHERE phone_number = %s
                    """,
                    (contact,)
                )

                existing = cursor.fetchone()

                if existing:

                    flash(
                        "Parent account already exists."
                    )

                    return redirect(
                        url_for("signup")
                    )

                cursor.execute(
                    """
                    INSERT INTO parents
                    (
                        full_name,
                        phone_number,
                        password,
                        preferred_language
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        full_name,
                        contact,
                        password,
                        "English"
                    )
                )

            else:

                flash(
                    "Only Parent and Teacher signup is available."
                )

                return redirect(
                    url_for("signup")
                )

            db.commit()

            flash(
                "Account created successfully! Please login."
            )

            return redirect(
                url_for("login")
            )

        except mysql.connector.Error as error:

            db.rollback()

            flash(
                "Database error: " + str(error)
            )

            return redirect(
                url_for("signup")
            )

        finally:

            cursor.close()
            db.close()

    return render_template(
        "signup.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out."
    )

    return redirect(
        url_for("home")
    )


# =========================================================
# TEACHER DASHBOARD
# =========================================================

@app.route("/teacher")
def teacher_dashboard():

    teacher_id = session.get(
        "teacher_id"
    )

    if not teacher_id:

        return redirect(
            url_for("login")
        )

    try:

        dashboard_data = (
            get_teacher_dashboard_data(
                teacher_id
            )
        )

        return render_template(
            "teacher_dashboard.html",
            **dashboard_data
        )

    except mysql.connector.Error as error:

        flash(
            "Database error: " + str(error)
        )

        return redirect(
            url_for("login")
        )


# =========================================================
# PARENT DASHBOARD
# =========================================================

@app.route("/parent")
def parent_dashboard():

    parent_id = session.get(
        "parent_id"
    )

    if not parent_id:

        return redirect(
            url_for("login")
        )

    try:

        dashboard_data = (
            get_parent_dashboard_data(
                parent_id
            )
        )

        return render_template(
            "parent_dashboard.html",
            **dashboard_data
        )

    except mysql.connector.Error as error:

        flash(
            "Database error: " + str(error)
        )

        return redirect(
            url_for("login")
        )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin")
def admin_dashboard():

    if not session.get("admin_id"):

        return redirect(
            url_for("login")
        )

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        # -------------------------------------------------
        # TEACHERS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT *
            FROM teachers
            ORDER BY teacher_id
            """
        )

        teachers = cursor.fetchall()

        # -------------------------------------------------
        # PARENTS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT *
            FROM parents
            ORDER BY parent_id
            """
        )

        parents = cursor.fetchall()

        # -------------------------------------------------
        # STUDENTS + PARENTS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                s.student_id,
                s.student_name,
                s.roll_number,
                s.class,
                s.parent_id,
                p.full_name AS parent_name

            FROM students s

            LEFT JOIN parents p
                ON s.parent_id = p.parent_id

            ORDER BY
                s.roll_number,
                s.student_name
            """
        )

        students = cursor.fetchall()

        # -------------------------------------------------
        # SCHEMES
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT *
            FROM schemes
            ORDER BY scheme_id
            """
        )

        schemes = cursor.fetchall()

        return render_template(
            "admin_dashboard.html",

            teachers=teachers,

            parents=parents,

            students=students,

            schemes=schemes,

            project_class=PROJECT_CLASS
        )

    finally:

        cursor.close()
        db.close()


# =========================================================
# ADD TEACHER
# =========================================================

@app.route(
    "/admin/add-teacher",
    methods=["POST"]
)
def add_teacher():

    if not session.get("admin_id"):

        return redirect(
            url_for("login")
        )

    full_name = request.form.get(
        "full_name",
        ""
    ).strip()

    username = request.form.get(
        "username",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    )

    class_assigned = request.form.get(
        "class_assigned",
        ""
    ).strip()

    if not full_name:

        full_name = username

    # If the form sends no class, use Class 10th.
    if not class_assigned:
        class_assigned = PROJECT_CLASS

    if (
        not username
        or not password
    ):

        flash(
            "Please fill in the teacher details."
        )

        return redirect(
            url_for("admin_dashboard")
        )

    db = get_db_connection()
    cursor = db.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO teachers
            (
                full_name,
                username,
                password,
                class_assigned
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                full_name,
                username,
                password,
                class_assigned
            )
        )

        db.commit()

        flash(
            "Teacher added successfully."
        )

    except mysql.connector.Error as error:

        db.rollback()

        flash(
            "Could not add teacher: " + str(error)
        )

    finally:

        cursor.close()
        db.close()

    return redirect(
        url_for("admin_dashboard")
    )


# =========================================================
# ADD PARENT
# =========================================================

@app.route(
    "/admin/add-parent",
    methods=["POST"]
)
def add_parent():

    if not session.get("admin_id"):

        return redirect(
            url_for("login")
        )

    full_name = request.form.get(
        "full_name",
        ""
    ).strip()

    phone_number = request.form.get(
        "phone_number",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    )

    language = request.form.get(
        "preferred_language",
        "English"
    )

    if (
        not full_name
        or not phone_number
        or not password
    ):

        flash(
            "Please fill in the parent details."
        )

        return redirect(
            url_for("admin_dashboard")
        )

    db = get_db_connection()
    cursor = db.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO parents
            (
                full_name,
                phone_number,
                password,
                preferred_language
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                full_name,
                phone_number,
                password,
                language
            )
        )

        db.commit()

        flash(
            "Parent added successfully."
        )

    except mysql.connector.Error as error:

        db.rollback()

        flash(
            "Could not add parent: " + str(error)
        )

    finally:

        cursor.close()
        db.close()

    return redirect(
        url_for("admin_dashboard")
    )


# =========================================================
# ADD STUDENT
# =========================================================

@app.route(
    "/admin/add-student",
    methods=["GET", "POST"]
)
def add_student():

    if not session.get("admin_id"):

        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        student_name = request.form.get(
            "student_name",
            ""
        ).strip()

        roll_number = request.form.get(
            "roll_number",
            ""
        ).strip()

        student_class = request.form.get(
            "class",
            ""
        ).strip()

        parent_id = request.form.get(
            "parent_id",
            ""
        ).strip()

        if not student_class:
            student_class = PROJECT_CLASS

        if (
            not student_name
            or not roll_number
            or not parent_id
        ):

            flash(
                "Please fill in all student details."
            )

            return redirect(
                url_for("add_student")
            )

        db = get_db_connection()
        cursor = db.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO students
                (
                    student_name,
                    roll_number,
                    class,
                    parent_id
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    student_name,
                    roll_number,
                    student_class,
                    parent_id
                )
            )

            db.commit()

            flash(
                "Student added successfully!"
            )

        except mysql.connector.Error as error:

            db.rollback()

            flash(
                "Could not add student: " + str(error)
            )

        finally:

            cursor.close()
            db.close()

        return redirect(
            url_for("admin_dashboard")
        )

    # -----------------------------------------------------
    # PARENT DROPDOWN
    # -----------------------------------------------------

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                parent_id,
                full_name
            FROM parents
            ORDER BY full_name
            """
        )

        parents = cursor.fetchall()

    finally:

        cursor.close()
        db.close()

    return render_template(
        "admin/add_student.html",
        parents=parents,
        project_class=PROJECT_CLASS
    )


# =========================================================
# ADD SCHEME
# =========================================================

@app.route(
    "/admin/add-scheme",
    methods=["GET", "POST"]
)
def add_scheme():

    if not session.get("admin_id"):

        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        scheme_name = request.form.get(
            "scheme_name",
            ""
        ).strip()

        eligible_class = request.form.get(
            "eligible_class",
            ""
        ).strip()

        deadline = request.form.get(
            "deadline",
            ""
        ).strip()

        documents_required = request.form.get(
            "documents_required",
            ""
        ).strip()

        if not eligible_class:
            eligible_class = PROJECT_CLASS

        if (
            not scheme_name
            or not deadline
            or not documents_required
        ):

            flash(
                "Please fill in all scheme details."
            )

            return redirect(
                url_for("add_scheme")
            )

        db = get_db_connection()
        cursor = db.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO schemes
                (
                    scheme_name,
                    eligible_class,
                    deadline,
                    documents_required
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    scheme_name,
                    eligible_class,
                    deadline,
                    documents_required
                )
            )

            db.commit()

            flash(
                "Scheme added successfully!"
            )

        except mysql.connector.Error as error:

            db.rollback()

            flash(
                "Could not add scheme: " + str(error)
            )

        finally:

            cursor.close()
            db.close()

        return redirect(
            url_for("admin_dashboard")
        )

    return render_template(
        "admin/add_scheme.html",
        project_class=PROJECT_CLASS
    )


# =========================================================
# DELETE TEACHER
# =========================================================

@app.route(
    "/admin/delete-teacher/<int:teacher_id>",
    methods=["POST"]
)
def delete_teacher(teacher_id):

    if not session.get("admin_id"):

        return redirect(
            url_for("login")
        )

    db = get_db_connection()
    cursor = db.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM teachers
            WHERE teacher_id = %s
            """,
            (teacher_id,)
        )

        db.commit()

        flash(
            "Teacher deleted successfully."
        )

    except mysql.connector.Error as error:

        db.rollback()

        flash(
            "Could not delete teacher: " + str(error)
        )

    finally:

        cursor.close()
        db.close()

    return redirect(
        url_for("admin_dashboard")
    )


# =========================================================
# DELETE PARENT
# =========================================================

@app.route(
    "/admin/delete-parent/<int:parent_id>",
    methods=["POST"]
)
def delete_parent(parent_id):

    if not session.get("admin_id"):

        return redirect(
            url_for("login")
        )

    db = get_db_connection()
    cursor = db.cursor()

    try:

        cursor.execute(
            """
            SELECT student_id
            FROM students
            WHERE parent_id = %s
            """,
            (parent_id,)
        )

        students = cursor.fetchall()

        for student in students:

            student_id = student[0]

            cursor.execute(
                """
                DELETE FROM attendance
                WHERE student_id = %s
                """,
                (student_id,)
            )

            cursor.execute(
                """
                DELETE FROM marks
                WHERE student_id = %s
                """,
                (student_id,)
            )

        cursor.execute(
            """
            DELETE FROM students
            WHERE parent_id = %s
            """,
            (parent_id,)
        )

        cursor.execute(
            """
            DELETE FROM parents
            WHERE parent_id = %s
            """,
            (parent_id,)
        )

        db.commit()

        flash(
            "Parent and linked student data deleted successfully."
        )

    except mysql.connector.Error as error:

        db.rollback()

        flash(
            "Could not delete parent: " + str(error)
        )

    finally:

        cursor.close()
        db.close()

    return redirect(
        url_for("admin_dashboard")
    )


# =========================================================
# DELETE STUDENT
# =========================================================

@app.route(
    "/admin/delete-student/<int:student_id>",
    methods=["POST"]
)
def delete_student(student_id):

    if not session.get("admin_id"):

        return redirect(
            url_for("login")
        )

    db = get_db_connection()
    cursor = db.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM attendance
            WHERE student_id = %s
            """,
            (student_id,)
        )

        cursor.execute(
            """
            DELETE FROM marks
            WHERE student_id = %s
            """,
            (student_id,)
        )

        cursor.execute(
            """
            DELETE FROM students
            WHERE student_id = %s
            """,
            (student_id,)
        )

        db.commit()

        flash(
            "Student deleted successfully."
        )

    except mysql.connector.Error as error:

        db.rollback()

        flash(
            "Could not delete student: " + str(error)
        )

    finally:

        cursor.close()
        db.close()

    return redirect(
        url_for("admin_dashboard")
    )


# =========================================================
# DELETE SCHEME
# =========================================================

@app.route(
    "/admin/delete-scheme/<int:scheme_id>",
    methods=["POST"]
)
def delete_scheme(scheme_id):

    if not session.get("admin_id"):

        return redirect(
            url_for("login")
        )

    db = get_db_connection()
    cursor = db.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM schemes
            WHERE scheme_id = %s
            """,
            (scheme_id,)
        )

        db.commit()

        flash(
            "Scheme deleted successfully."
        )

    except mysql.connector.Error as error:

        db.rollback()

        flash(
            "Could not delete scheme: " + str(error)
        )

    finally:

        cursor.close()
        db.close()

    return redirect(
        url_for("admin_dashboard")
    )


# =========================================================
# ATTENDANCE PAGE
# =========================================================

@app.route(
    "/attendance",
    methods=["GET", "POST"]
)
def attendance():

    # -----------------------------------------------------
    # WHO IS USING THE PAGE?
    # -----------------------------------------------------

    role = session.get("role")

    # -----------------------------------------------------
    # ATTENDANCE DATE
    # -----------------------------------------------------

    if request.method == "POST":

        selected_date = (
            request.form.get(
                "attendance_date",
                ""
            ).strip()
        )

    else:

        selected_date = (
            request.args.get(
                "date",
                ""
            ).strip()
        )

    if not selected_date:

        selected_date = date.today().isoformat()

    # -----------------------------------------------------
    # GET STUDENTS
    # -----------------------------------------------------

    try:

        students = get_students_for_current_user()

    except mysql.connector.Error as error:

        flash(
            "Database error: " + str(error)
        )

        return render_template(
            "attendance.html",
            students=[],
            total_students=0,
            present_count=0,
            absent_count=0,
            attendance_percentage=0,
            selected_date=selected_date,
            project_class=PROJECT_CLASS
        )

    # -----------------------------------------------------
    # SAVE ATTENDANCE
    # -----------------------------------------------------

    if request.method == "POST":

        if role not in ("teacher", "admin"):

            flash(
                "Only teachers can save attendance."
            )

            return redirect(
                url_for("attendance")
            )

        db = get_db_connection()
        cursor = db.cursor()

        try:

            for student in students:

                student_id = (
                    student["student_id"]
                )

                field_name = (
                    "status_" +
                    str(student_id)
                )

                status = (
                    request.form.get(
                        field_name,
                        ""
                    ).strip()
                )

                if status not in (
                    "Present",
                    "Absent"
                ):
                    continue

                cursor.execute(
                    """
                    DELETE FROM attendance
                    WHERE student_id = %s
                    AND attendance_date = %s
                    """,
                    (
                        student_id,
                        selected_date
                    )
                )

                cursor.execute(
                    """
                    INSERT INTO attendance
                    (
                        student_id,
                        attendance_date,
                        status
                    )
                    VALUES (%s, %s, %s)
                    """,
                    (
                        student_id,
                        selected_date,
                        status
                    )
                )

            db.commit()

            flash(
                "Attendance saved successfully."
            )

            return redirect(
                url_for(
                    "attendance",
                    date=selected_date
                )
            )

        except mysql.connector.Error as error:

            db.rollback()

            flash(
                "Could not save attendance: " +
                str(error)
            )

        finally:

            cursor.close()
            db.close()

    # -----------------------------------------------------
    # LOAD ATTENDANCE FOR SELECTED DATE
    # -----------------------------------------------------

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        if students:

            student_ids = [
                student["student_id"]
                for student in students
            ]

            placeholders = ",".join(
                ["%s"] * len(student_ids)
            )

            query = f"""
                SELECT
                    attendance_id,
                    student_id,
                    attendance_date,
                    status
                FROM attendance
                WHERE attendance_date = %s
                AND student_id IN ({placeholders})
                ORDER BY attendance_id DESC
            """

            cursor.execute(
                query,
                [selected_date] + student_ids
            )

            attendance_rows = (
                cursor.fetchall()
            )

        else:

            attendance_rows = []

        status_by_student = {}

        for record in attendance_rows:

            student_id = record["student_id"]

            if student_id not in status_by_student:

                status_by_student[student_id] = (
                    record["status"]
                )

        for student in students:

            student["attendance_status"] = (
                status_by_student.get(
                    student["student_id"],
                    ""
                )
            )

        total_students = len(
            students
        )

        present_count = 0
        absent_count = 0

        for student in students:

            status = str(
                student.get(
                    "attendance_status",
                    ""
                )
            ).strip().lower()

            if status == "present":

                present_count += 1

            elif status == "absent":

                absent_count += 1

        if total_students > 0:

            attendance_percentage = round(
                (
                    present_count /
                    total_students
                ) * 100,
                1
            )

        else:

            attendance_percentage = 0

        return render_template(
            "attendance.html",

            students=students,

            total_students=total_students,

            present_count=present_count,

            absent_count=absent_count,

            attendance_percentage=(
                attendance_percentage
            ),

            selected_date=selected_date,

            project_class=PROJECT_CLASS
        )

    finally:

        cursor.close()
        db.close()


# =========================================================
# SCHEMES PAGE
# =========================================================

@app.route("/schemes")
def schemes():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        try:

            cursor.execute(
                """
                SELECT *
                FROM schemes
                ORDER BY scheme_id
                """
            )

            schemes_data = (
                cursor.fetchall()
            )

        except mysql.connector.Error:

            schemes_data = []

        return render_template(
            "schemes.html",
            schemes=schemes_data,
            project_class=PROJECT_CLASS
        )

    finally:

        cursor.close()
        db.close()


# =========================================================
# MARKS PAGE
# =========================================================

@app.route(
    "/marks",
    methods=["GET", "POST"]
)
def marks():

    role = session.get("role")

    # -----------------------------------------------------
    # GET STUDENTS
    # -----------------------------------------------------

    try:

        students = get_students_for_current_user()

    except mysql.connector.Error as error:

        flash(
            "Database error: " + str(error)
        )

        return render_template(
            "marks.html",
            students=[],
            total_students=0,
            total_subjects=3,
            maximum_marks=100,
            project_class=PROJECT_CLASS
        )

    # -----------------------------------------------------
    # SAVE MARKS
    # -----------------------------------------------------

    if request.method == "POST":

        if role not in ("teacher", "admin"):

            flash(
                "Only teachers can save marks."
            )

            return redirect(
                url_for("marks")
            )

        db = get_db_connection()
        cursor = db.cursor()

        try:

            subjects = {
                "mathematics": "Mathematics",
                "science": "Science",
                "english": "English"
            }

            for student in students:

                student_id = (
                    student["student_id"]
                )

                cursor.execute(
                    """
                    DELETE FROM marks
                    WHERE student_id = %s
                    AND LOWER(subject) IN (
                        'mathematics',
                        'science',
                        'english'
                    )
                    """,
                    (student_id,)
                )

                for field_key, subject_name in (
                    subjects.items()
                ):

                    field_name = (
                        "marks_"
                        + str(student_id)
                        + "_"
                        + field_key
                    )

                    raw_value = (
                        request.form.get(
                            field_name,
                            ""
                        ).strip()
                    )

                    if raw_value == "":
                        continue

                    try:

                        marks_value = int(
                            raw_value
                        )

                    except ValueError:

                        continue

                    if marks_value < 0:
                        marks_value = 0

                    if marks_value > 100:
                        marks_value = 100

                    cursor.execute(
                        """
                        INSERT INTO marks
                        (
                            student_id,
                            subject,
                            marks_obtained
                        )
                        VALUES (%s, %s, %s)
                        """,
                        (
                            student_id,
                            subject_name,
                            marks_value
                        )
                    )

            db.commit()

            flash(
                "Marks saved successfully."
            )

            return redirect(
                url_for("marks")
            )

        except mysql.connector.Error as error:

            db.rollback()

            flash(
                "Could not save marks: " +
                str(error)
            )

        finally:

            cursor.close()
            db.close()

    # -----------------------------------------------------
    # LOAD MARKS FOR STUDENTS
    # -----------------------------------------------------

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        if students:

            student_ids = [
                student["student_id"]
                for student in students
            ]

            placeholders = ",".join(
                ["%s"] * len(student_ids)
            )

            query = f"""
                SELECT
                    student_id,
                    subject,
                    marks_obtained
                FROM marks
                WHERE student_id IN ({placeholders})
                ORDER BY marks_id DESC
            """

            cursor.execute(
                query,
                student_ids
            )

            mark_rows = (
                cursor.fetchall()
            )

        else:

            student_ids = []
            mark_rows = []

        # -------------------------------------------------
        # DEFAULT VALUES FOR EACH STUDENT
        # -------------------------------------------------

        marks_by_student = {}

        for student_id in student_ids:

            marks_by_student[student_id] = {
                "mathematics": "",
                "science": "",
                "english": ""
            }

        # -------------------------------------------------
        # PUT DATABASE MARKS INTO THE CORRECT SUBJECT
        # -------------------------------------------------

        for row in mark_rows:

            student_id = row["student_id"]

            subject = str(
                row.get("subject", "")
            ).strip().lower()

            if student_id not in marks_by_student:

                marks_by_student[student_id] = {
                    "mathematics": "",
                    "science": "",
                    "english": ""
                }

            if subject == "mathematics":

                if marks_by_student[
                    student_id
                ]["mathematics"] == "":

                    marks_by_student[
                        student_id
                    ]["mathematics"] = (
                        row["marks_obtained"]
                    )

            elif subject == "science":

                if marks_by_student[
                    student_id
                ]["science"] == "":

                    marks_by_student[
                        student_id
                    ]["science"] = (
                        row["marks_obtained"]
                    )

            elif subject == "english":

                if marks_by_student[
                    student_id
                ]["english"] == "":

                    marks_by_student[
                        student_id
                    ]["english"] = (
                        row["marks_obtained"]
                    )

        # -------------------------------------------------
        # CALCULATE TOTAL + AVERAGE
        # -------------------------------------------------

        for student in students:

            student_id = (
                student["student_id"]
            )

            saved_marks = (
                marks_by_student.get(
                    student_id,
                    {
                        "mathematics": "",
                        "science": "",
                        "english": ""
                    }
                )
            )

            student["mathematics"] = (
                saved_marks["mathematics"]
            )

            student["science"] = (
                saved_marks["science"]
            )

            student["english"] = (
                saved_marks["english"]
            )

            numeric_values = []

            for value in (
                student["mathematics"],
                student["science"],
                student["english"]
            ):

                if value == "":
                    continue

                try:

                    numeric_values.append(
                        float(value)
                    )

                except (
                    TypeError,
                    ValueError
                ):

                    pass

            if numeric_values:

                total = sum(
                    numeric_values
                )

                average = (
                    total /
                    len(numeric_values)
                )

                if total.is_integer():

                    student["total_marks"] = int(
                        total
                    )

                else:

                    student["total_marks"] = (
                        round(total, 1)
                    )

                student["average_marks"] = (
                    round(average, 1)
                )

            else:

                student["total_marks"] = 0

                student["average_marks"] = 0

        # -------------------------------------------------
        # PAGE SUMMARY
        # -------------------------------------------------

        total_students = len(
            students
        )

        total_subjects = 3

        maximum_marks = 100

        return render_template(
            "marks.html",

            students=students,

            total_students=total_students,

            total_subjects=total_subjects,

            maximum_marks=maximum_marks,

            project_class=PROJECT_CLASS
        )

    finally:

        cursor.close()
        db.close()


# =========================================================
# MULTILINGUAL PAGE
# =========================================================

@app.route("/multilingual")
def multilingual():

    return render_template(
        "multilingual.html",
        project_class=PROJECT_CLASS
    )


# =========================================================
# TEACHER VOICE MESSAGE PAGE
# =========================================================

@app.route("/voicemail")
def voicemail():

    # -----------------------------------------------------
    # TEACHER
    # -----------------------------------------------------

    if session.get("teacher_id"):

        ensure_messages_table()

        return render_template(
            "voicemail.html",
            project_class=PROJECT_CLASS
        )

    # -----------------------------------------------------
    # PARENT
    # -----------------------------------------------------

    if session.get("parent_id"):

        return redirect(
            url_for("parent_voicemail")
        )

    # -----------------------------------------------------
    # NOT LOGGED IN
    # -----------------------------------------------------

    return redirect(
        url_for("login")
    )


# =========================================================
# PARENT VOICE MESSAGE PAGE
# =========================================================

@app.route("/parent/voicemail")
def parent_voicemail():

    parent_id = session.get(
        "parent_id"
    )

    if not parent_id:

        return redirect(
            url_for("login")
        )

    try:

        ensure_messages_table()

        student, teacher = (
            get_parent_teacher(
                parent_id
            )
        )

        return render_template(
            "parent_voicemail.html",
            student=student,
            teacher=teacher,
            project_class=PROJECT_CLASS
        )

    except mysql.connector.Error as error:

        flash(
            "Database error: " + str(error)
        )

        return redirect(
            url_for("parent_dashboard")
        )


# =========================================================
# PARENT MESSAGE API
# =========================================================

@app.route(
    "/api/parent/messages",
    methods=["GET"]
)
def parent_messages_api():

    parent_id = session.get(
        "parent_id"
    )

    if not parent_id:

        return jsonify({
            "success": False,
            "message": "Parent login required."
        }), 401

    ensure_messages_table()

    student, teacher = (
        get_parent_teacher(
            parent_id
        )
    )

    if not teacher:

        return jsonify({
            "success": True,
            "teacher": None,
            "student": student,
            "messages": []
        })

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                message_id,
                parent_id,
                teacher_id,
                sender_role,
                message_type,
                message_text,
                audio_path,
                is_read,
                created_at
            FROM messages
            WHERE parent_id = %s
            AND teacher_id = %s
            ORDER BY created_at ASC
            """,
            (
                parent_id,
                teacher["teacher_id"]
            )
        )

        messages = cursor.fetchall()

        cursor.execute(
            """
            UPDATE messages
            SET is_read = 1
            WHERE parent_id = %s
            AND teacher_id = %s
            AND sender_role = 'teacher'
            """,
            (
                parent_id,
                teacher["teacher_id"]
            )
        )

        db.commit()

        return jsonify({
            "success": True,
            "teacher": teacher,
            "student": student,
            "messages": [
                serialize_message(
                    message
                )
                for message in messages
            ]
        })

    finally:

        cursor.close()
        db.close()


# =========================================================
# PARENT TEXT MESSAGE API
# =========================================================

@app.route(
    "/api/parent/message",
    methods=["POST"]
)
def parent_send_message():

    parent_id = session.get(
        "parent_id"
    )

    if not parent_id:

        return jsonify({
            "success": False,
            "message": "Parent login required."
        }), 401

    data = request.get_json(
        silent=True
    ) or {}

    message_text = str(
        data.get(
            "message_text",
            ""
        )
    ).strip()

    if not message_text:

        return jsonify({
            "success": False,
            "message": "Message cannot be empty."
        }), 400

    ensure_messages_table()

    student, teacher = (
        get_parent_teacher(
            parent_id
        )
    )

    if not teacher:

        return jsonify({
            "success": False,
            "message": "No teacher is assigned to your child's class."
        }), 400

    db = get_db_connection()
    cursor = db.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO messages
            (
                parent_id,
                teacher_id,
                sender_role,
                message_type,
                message_text
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                parent_id,
                teacher["teacher_id"],
                "parent",
                "text",
                message_text
            )
        )

        db.commit()

        return jsonify({
            "success": True
        })

    finally:

        cursor.close()
        db.close()


# =========================================================
# PARENT VOICE MESSAGE API
# =========================================================

@app.route(
    "/api/parent/voice",
    methods=["POST"]
)
def parent_send_voice():

    parent_id = session.get(
        "parent_id"
    )

    if not parent_id:

        return jsonify({
            "success": False,
            "message": "Parent login required."
        }), 401

    audio_file = request.files.get(
        "audio"
    )

    if not audio_file:

        return jsonify({
            "success": False,
            "message": "No audio file received."
        }), 400

    ensure_messages_table()

    student, teacher = (
        get_parent_teacher(
            parent_id
        )
    )

    if not teacher:

        return jsonify({
            "success": False,
            "message": "No teacher is assigned to your child's class."
        }), 400

    original_filename = (
        audio_file.filename or ""
    )

    if "." in original_filename:

        extension = (
            original_filename.rsplit(
                ".",
                1
            )[1].lower()
        )

    else:

        extension = "webm"

    if extension not in ALLOWED_AUDIO_EXTENSIONS:

        extension = "webm"

    unique_name = (
        uuid.uuid4().hex
        + "."
        + extension
    )

    unique_name = secure_filename(
        unique_name
    )

    save_path = os.path.join(
        VOICE_UPLOAD_FOLDER,
        unique_name
    )

    audio_file.save(
        save_path
    )

    relative_audio_path = os.path.join(
        "uploads",
        "voice_messages",
        unique_name
    ).replace("\\", "/")

    db = get_db_connection()
    cursor = db.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO messages
            (
                parent_id,
                teacher_id,
                sender_role,
                message_type,
                audio_path
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                parent_id,
                teacher["teacher_id"],
                "parent",
                "voice",
                relative_audio_path
            )
        )

        db.commit()

        return jsonify({
            "success": True,
            "audio_url": url_for(
                "static",
                filename=relative_audio_path
            )
        })

    except mysql.connector.Error:

        if os.path.exists(save_path):

            os.remove(
                save_path
            )

        raise

    finally:

        cursor.close()
        db.close()


# =========================================================
# TEACHER CONVERSATION API
# =========================================================

@app.route(
    "/api/teacher/conversations",
    methods=["GET"]
)
def teacher_conversations_api():

    teacher_id = session.get(
        "teacher_id"
    )

    if not teacher_id:

        return jsonify({
            "success": False,
            "message": "Teacher login required."
        }), 401

    ensure_messages_table()

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT DISTINCT
                p.parent_id,
                p.full_name AS parent_name,
                p.phone_number,
                s.student_id,
                s.student_name,
                s.class

            FROM parents p

            INNER JOIN students s
                ON s.parent_id = p.parent_id

            INNER JOIN teachers t
                ON TRIM(t.class_assigned)
                = TRIM(s.class)

            WHERE t.teacher_id = %s

            ORDER BY p.full_name
            """,
            (teacher_id,)
        )

        conversations = cursor.fetchall()

        return jsonify({
            "success": True,
            "conversations": conversations
        })

    finally:

        cursor.close()
        db.close()


# =========================================================
# TEACHER CONVERSATION MESSAGE API
# =========================================================

@app.route(
    "/api/teacher/messages/<int:parent_id>",
    methods=["GET"]
)
def teacher_messages_api(parent_id):

    teacher_id = session.get(
        "teacher_id"
    )

    if not teacher_id:

        return jsonify({
            "success": False,
            "message": "Teacher login required."
        }), 401

    ensure_messages_table()

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        # -------------------------------------------------
        # VERIFY CONNECTION
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                p.parent_id,
                p.full_name AS parent_name,
                s.student_id,
                s.student_name,
                s.class

            FROM parents p

            INNER JOIN students s
                ON s.parent_id = p.parent_id

            INNER JOIN teachers t
                ON TRIM(t.class_assigned)
                = TRIM(s.class)

            WHERE p.parent_id = %s
            AND t.teacher_id = %s

            LIMIT 1
            """,
            (
                parent_id,
                teacher_id
            )
        )

        parent_connection = (
            cursor.fetchone()
        )

        if not parent_connection:

            return jsonify({
                "success": False,
                "message": "This parent is not connected to this teacher."
            }), 403

        # -------------------------------------------------
        # GET MESSAGES
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                message_id,
                parent_id,
                teacher_id,
                sender_role,
                message_type,
                message_text,
                audio_path,
                is_read,
                created_at
            FROM messages
            WHERE parent_id = %s
            AND teacher_id = %s
            ORDER BY created_at ASC
            """,
            (
                parent_id,
                teacher_id
            )
        )

        messages = cursor.fetchall()

        # -------------------------------------------------
        # MARK PARENT MESSAGES AS READ
        # -------------------------------------------------

        cursor.execute(
            """
            UPDATE messages
            SET is_read = 1
            WHERE parent_id = %s
            AND teacher_id = %s
            AND sender_role = 'parent'
            """,
            (
                parent_id,
                teacher_id
            )
        )

        db.commit()

        return jsonify({
            "success": True,
            "parent": parent_connection,
            "messages": [
                serialize_message(message)
                for message in messages
            ]
        })

    finally:

        cursor.close()
        db.close()


# =========================================================
# TEACHER TEXT MESSAGE API
# =========================================================

@app.route(
    "/api/teacher/message",
    methods=["POST"]
)
def teacher_send_message():

    teacher_id = session.get(
        "teacher_id"
    )

    if not teacher_id:

        return jsonify({
            "success": False,
            "message": "Teacher login required."
        }), 401

    data = request.get_json(
        silent=True
    ) or {}

    parent_id = data.get(
        "parent_id"
    )

    message_text = str(
        data.get(
            "message_text",
            ""
        )
    ).strip()

    if not parent_id or not message_text:

        return jsonify({
            "success": False,
            "message": "Parent and message are required."
        }), 400

    ensure_messages_table()

    db = get_db_connection()
    cursor = db.cursor()

    try:

        cursor.execute(
            """
            SELECT s.student_id

            FROM students s

            INNER JOIN teachers t
                ON TRIM(s.class)
                = TRIM(t.class_assigned)

            WHERE s.parent_id = %s
            AND t.teacher_id = %s

            LIMIT 1
            """,
            (
                parent_id,
                teacher_id
            )
        )

        connection = cursor.fetchone()

        if not connection:

            return jsonify({
                "success": False,
                "message": "This parent is not connected to your class."
            }), 403

        cursor.execute(
            """
            INSERT INTO messages
            (
                parent_id,
                teacher_id,
                sender_role,
                message_type,
                message_text
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                parent_id,
                teacher_id,
                "teacher",
                "text",
                message_text
            )
        )

        db.commit()

        return jsonify({
            "success": True
        })

    finally:

        cursor.close()
        db.close()


# =========================================================
# TEACHER VOICE MESSAGE API
# =========================================================

@app.route(
    "/api/teacher/voice",
    methods=["POST"]
)
def teacher_send_voice():

    teacher_id = session.get(
        "teacher_id"
    )

    if not teacher_id:

        return jsonify({
            "success": False,
            "message": "Teacher login required."
        }), 401

    parent_id = request.form.get(
        "parent_id"
    )

    audio_file = request.files.get(
        "audio"
    )

    if not parent_id or not audio_file:

        return jsonify({
            "success": False,
            "message": "Parent and audio file are required."
        }), 400

    ensure_messages_table()

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        # -------------------------------------------------
        # VERIFY PARENT CONNECTION
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT s.student_id

            FROM students s

            INNER JOIN teachers t
                ON TRIM(s.class)
                = TRIM(t.class_assigned)

            WHERE s.parent_id = %s
            AND t.teacher_id = %s

            LIMIT 1
            """,
            (
                parent_id,
                teacher_id
            )
        )

        connection = cursor.fetchone()

        if not connection:

            return jsonify({
                "success": False,
                "message": "This parent is not connected to your class."
            }), 403

        # -------------------------------------------------
        # FILE EXTENSION
        # -------------------------------------------------

        original_filename = (
            audio_file.filename or ""
        )

        if "." in original_filename:

            extension = (
                original_filename.rsplit(
                    ".",
                    1
                )[1].lower()
            )

        else:

            extension = "webm"

        if extension not in ALLOWED_AUDIO_EXTENSIONS:

            extension = "webm"

        unique_name = (
            uuid.uuid4().hex
            + "."
            + extension
        )

        unique_name = secure_filename(
            unique_name
        )

        save_path = os.path.join(
            VOICE_UPLOAD_FOLDER,
            unique_name
        )

        audio_file.save(
            save_path
        )

        relative_audio_path = os.path.join(
            "uploads",
            "voice_messages",
            unique_name
        ).replace("\\", "/")

        # -------------------------------------------------
        # SAVE MESSAGE
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO messages
            (
                parent_id,
                teacher_id,
                sender_role,
                message_type,
                audio_path
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                parent_id,
                teacher_id,
                "teacher",
                "voice",
                relative_audio_path
            )
        )

        db.commit()

        return jsonify({
            "success": True,
            "audio_url": url_for(
                "static",
                filename=relative_audio_path
            )
        })

    except mysql.connector.Error:

        if "save_path" in locals():

            if os.path.exists(save_path):

                os.remove(
                    save_path
                )

        raise

    finally:

        cursor.close()
        db.close()


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )