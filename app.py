# =========================================================
# REAL-LIFE STUDENT MANAGEMENT SYSTEM
# Streamlit + SQLite
# =========================================================

import streamlit as st
import sqlite3
import pandas as pd
import hashlib
from datetime import datetime

# =========================================================
# DATABASE CONNECTION
# =========================================================

conn = sqlite3.connect("students.db", check_same_thread=False)
cursor = conn.cursor()

# =========================================================
# DATABASE TABLES
# =========================================================

# Students table (core entity)
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    department TEXT,
    year INTEGER,
    status TEXT DEFAULT 'ACTIVE',
    created_at TEXT,
    updated_at TEXT
)
""")

# Attendance table (real-life feature)
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    date TEXT,
    status TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id)
)
""")

# Marks table
cursor.execute("""
CREATE TABLE IF NOT EXISTS marks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    subject TEXT,
    marks INTEGER,
    FOREIGN KEY (student_id) REFERENCES students(id)
)
""")

conn.commit()

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def current_time():
    """Returns current timestamp"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def fetch_students():
    """Fetch only active students"""
    cursor.execute("SELECT * FROM students WHERE status='ACTIVE'")
    return cursor.fetchall()

# =========================================================
# UI CONFIG
# =========================================================

st.title("🎓 Student Management System")

menu = [
    "Add Student",
    "View Students",
    "Search & Filter",
    "Attendance",
    "Marks",
    "Deactivate Student",
    "Export Data"
]

choice = st.sidebar.selectbox("Menu", menu)

# =========================================================
# ADD STUDENT
# =========================================================

if choice == "Add Student":
    st.subheader("Add New Student")

    name = st.text_input("Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    department = st.selectbox("Department", ["CSE", "AIML", "DS", "ECE"])
    year = st.selectbox("Year", [1, 2, 3, 4])

    if st.button("Save Student"):
        try:
            cursor.execute("""
                INSERT INTO students
                (name, email, phone, department, year, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, email, phone, department, year, current_time(), current_time()))
            conn.commit()
            st.success("Student added successfully")
        except:
            st.error("Email already exists")

# =========================================================
# VIEW STUDENTS
# =========================================================

elif choice == "View Students":
    st.subheader("All Active Students")

    data = fetch_students()
    df = pd.DataFrame(data, columns=[
        "ID", "Name", "Email", "Phone", "Dept", "Year",
        "Status", "Created", "Updated"
    ])
    st.dataframe(df)

# =========================================================
# SEARCH & FILTER
# =========================================================

elif choice == "Search & Filter":
    st.subheader("Search Students")

    keyword = st.text_input("Search by Name")
    dept = st.selectbox("Department", ["All", "CSE", "AIML", "DS", "ECE"])

    query = "SELECT * FROM students WHERE status='ACTIVE'"
    params = []

    if keyword:
        query += " AND name LIKE ?"
        params.append(f"%{keyword}%")

    if dept != "All":
        query += " AND department=?"
        params.append(dept)

    cursor.execute(query, params)
    results = cursor.fetchall()

    df = pd.DataFrame(results, columns=[
        "ID", "Name", "Email", "Phone", "Dept", "Year",
        "Status", "Created", "Updated"
    ])
    st.dataframe(df)

# =========================================================
# ATTENDANCE MODULE
# =========================================================

elif choice == "Attendance":
    st.subheader("Mark Attendance")

    students = fetch_students()
    ids = [s[0] for s in students]

    student_id = st.selectbox("Student ID", ids)
    status = st.selectbox("Attendance", ["PRESENT", "ABSENT"])

    if st.button("Submit Attendance"):
        cursor.execute("""
            INSERT INTO attendance (student_id, date, status)
            VALUES (?, ?, ?)
        """, (student_id, current_time(), status))
        conn.commit()
        st.success("Attendance recorded")

# =========================================================
# MARKS MODULE
# =========================================================

elif choice == "Marks":
    st.subheader("Add Student Marks")

    students = fetch_students()
    ids = [s[0] for s in students]

    student_id = st.selectbox("Student ID", ids)
    subject = st.text_input("Subject")
    marks = st.number_input("Marks", 0, 100)

    if st.button("Save Marks"):
        cursor.execute("""
            INSERT INTO marks (student_id, subject, marks)
            VALUES (?, ?, ?)
        """, (student_id, subject, marks))
        conn.commit()
        st.success("Marks added")

# =========================================================
# SOFT DELETE (DEACTIVATE)
# =========================================================

elif choice == "Deactivate Student":
    st.subheader("Deactivate Student")

    students = fetch_students()
    ids = [s[0] for s in students]

    student_id = st.selectbox("Student ID", ids)

    if st.button("Deactivate"):
        cursor.execute("""
            UPDATE students
            SET status='INACTIVE', updated_at=?
            WHERE id=?
        """, (current_time(), student_id))
        conn.commit()
        st.warning("Student deactivated (not deleted)")

# =========================================================
# EXPORT DATA
# =========================================================

elif choice == "Export Data":
    st.subheader("Export Student Data")

    data = fetch_students()
    df = pd.DataFrame(data, columns=[
        "ID", "Name", "Email", "Phone", "Dept", "Year",
        "Status", "Created", "Updated"
    ])

    st.download_button(
        "Download CSV",
        df.to_csv(index=False),
        file_name="students.csv"
    )
