
import sqlite3
from datetime import datetime

DB_NAME = "employee_data.db"

# ------------------ Initialize DB ------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Employee table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        joining_date TEXT,
        photo BLOB
    )
    """)

    # NEW structure for attendance: track IN and OUT per day
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id TEXT,
        name TEXT,
        date TEXT,
        punch_in TEXT,
        punch_out TEXT
    )
    """)

    conn.commit()
    conn.close()

# ------------------ Add Employee ------------------
def insert_employee(emp_id, name, joining_date, photo_blob):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO employees (emp_id, name, joining_date, photo) VALUES (?, ?, ?, ?)",
        (emp_id, name, joining_date, photo_blob)
    )
    conn.commit()
    conn.close()

# ------------------ Get All Employees ------------------
def get_all_employees():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT emp_id, name, photo FROM employees")
    data = cursor.fetchall()
    conn.close()
    return data

# ------------------ Mark Attendance (IN/OUT logic) ------------------
def mark_attendance(emp_id, name, punch_type):
    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Check if user already has a row for today
    cursor.execute("SELECT id, punch_in, punch_out FROM attendance WHERE emp_id = ? AND date = ?", (emp_id, today))
    row = cursor.fetchone()

    if row:
        record_id, punch_in, punch_out = row
        if punch_type == "IN" and not punch_in:
            cursor.execute("UPDATE attendance SET punch_in = ? WHERE id = ?", (current_time, record_id))
        elif punch_type == "OUT" and not punch_out:
            cursor.execute("UPDATE attendance SET punch_out = ? WHERE id = ?", (current_time, record_id))
    else:
        # Insert a new row with only punch_in or punch_out based on punch_type
        punch_in_time = current_time if punch_type == "IN" else None
        punch_out_time = current_time if punch_type == "OUT" else None

        cursor.execute("""
            INSERT INTO attendance (emp_id, name, date, punch_in, punch_out)
            VALUES (?, ?, ?, ?, ?)
        """, (emp_id, name, today, punch_in_time, punch_out_time))

    conn.commit()
    conn.close()
