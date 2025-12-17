# ---------------------------------------------------------
# REAL-LIFE STUDENT MANAGEMENT SYSTEM (SMS)
# USING STREAMLIT + SQLITE
# ---------------------------------------------------------

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ---------------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------------

conn = sqlite3.connect("students.db", check_same_thread=False)
cursor = conn.cursor()

# ---------------------------------------------------------
# DATABASE SCHEMA
# ---------------------------------------------------------

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

conn.commit()

# ---------------------------------------------------------
# UTILITY FUNCTIONS
# ---------------------------------------------------------

def fetch_students(filters=None):
    base_query = "SELECT * FROM students WHERE status='ACTIVE'"
    params = []

    if filters:
        for key, value in filters.items():
            base_query += f" AND {key}=?"
            params.append(value)

    cursor.execute(base_query, tuple(params))
    return cursor.fetchall()

def fetch_all_students():
    cursor.execute("SELECT * FROM students")
    return cursor.fetchall()

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="Student Management System",
    layout="wide"
)

st.title("🎓 Student Management System")

menu = [
    "Add Student",
    "View Students",
    "Search & Filter",
    "Update Student",
    "Deactivate Student"
]

choice = st.sidebar.selectbox("Menu", menu)

# ---------------------------------------------------------
# ADD STUDENT
# ---------------------------------------------------------

if choice == "Add Student":
    st.subheader("Add New Student")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    department = st.selectbox("Department", ["CSE", "AIML", "DS", "ECE"])
    year = st.selectbox("Academic Year", [1, 2, 3, 4])

    if st.button("Save Student"):
        if not name or not email:
            st.error("Name and Email are mandatory")
        else:
            try:
                cursor.execute("""
                INSERT INTO students 
                (name, email, phone, department, year, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    name, email, phone, department, year,
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                conn.commit()
                st.success("Student added successfully")
            except sqlite3.IntegrityError:
                st.error("Email already exists")

# ---------------------------------------------------------
# VIEW STUDENTS
# ---------------------------------------------------------

elif choice == "View Students":
    st.subheader("All Active Students")

    students = fetch_students()

    df = pd.DataFrame(
        students,
        columns=["ID", "Name", "Email", "Phone",
                 "Department", "Year", "Status",
                 "Created At", "Updated At"]
    )

    st.dataframe(df, use_container_width=True)

# ---------------------------------------------------------
# SEARCH & FILTER
# ---------------------------------------------------------

elif choice == "Search & Filter":
    st.subheader("Search & Filter Students")

    keyword = st.text_input("Search by Name")
    dept = st.selectbox("Department", ["All", "CSE", "AIML", "DS", "ECE"])
    year = st.selectbox("Year", ["All", 1, 2, 3, 4])

    base_query = "SELECT * FROM students WHERE status='ACTIVE'"
    conditions = []
    params = []

    if keyword.strip():
        conditions.append("name LIKE ?")
        params.append(f"%{keyword}%")

    if dept != "All":
        conditions.append("department=?")
        params.append(dept)

    if year != "All":
        conditions.append("year=?")
        params.append(year)

    if conditions:
        base_query += " AND " + " AND ".join(conditions)

    cursor.execute(base_query, tuple(params))
    results = cursor.fetchall()

    df = pd.DataFrame(
        results,
        columns=["ID", "Name", "Email", "Phone",
                 "Department", "Year", "Status",
                 "Created At", "Updated At"]
    )

    st.dataframe(df, use_container_width=True)

# ---------------------------------------------------------
# UPDATE STUDENT
# ---------------------------------------------------------

elif choice == "Update Student":
    st.subheader("Update Student")

    students = fetch_students()
    ids = [s[0] for s in students]

    student_id = st.selectbox("Select Student ID", ids)

    cursor.execute("SELECT * FROM students WHERE id=?", (student_id,))
    student = cursor.fetchone()

    name = st.text_input("Name", student[1])
    email = st.text_input("Email", student[2])
    phone = st.text_input("Phone", student[3])
    department = st.selectbox(
        "Department",
        ["CSE", "AIML", "DS", "ECE"],
        index=["CSE", "AIML", "DS", "ECE"].index(student[4])
    )
    year = st.selectbox("Year", [1, 2, 3, 4], index=student[5]-1)

    if st.button("Update"):
        cursor.execute("""
        UPDATE students SET
        name=?, email=?, phone=?, department=?, year=?, updated_at=?
        WHERE id=?
        """, (
            name, email, phone, department, year,
            datetime.now().isoformat(),
            student_id
        ))
        conn.commit()
        st.success("Student updated successfully")

# ---------------------------------------------------------
# DEACTIVATE STUDENT (SOFT DELETE)
# ---------------------------------------------------------

elif choice == "Deactivate Student":
    st.subheader("Deactivate Student")

    students = fetch_students()
    ids = [s[0] for s in students]

    student_id = st.selectbox("Select Student ID", ids)

    if st.button("Deactivate"):
        cursor.execute("""
        UPDATE students SET status='INACTIVE', updated_at=?
        WHERE id=?
        """, (datetime.now().isoformat(), student_id))
        conn.commit()
        st.warning("Student deactivated (soft delete)")

# ---------------------------------------------------------
# END OF APPLICATION
# ---------------------------------------------------------
