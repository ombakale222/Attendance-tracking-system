import sqlite3

DB_NAME = "employee_data.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Rename old table (backup)
cursor.execute("ALTER TABLE attendance RENAME TO attendance_old")

# Create new correct table
cursor.execute("""
CREATE TABLE attendance (
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

print("✅ Migration done. You now have 'attendance' table with punch_in/punch_out.")
