# =========================================================
# STUDENT MANAGEMENT SYSTEM (ERROR-PROOF)
# Streamlit + SQLite + Pandas
# =========================================================

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# =========================================================
# STREAMLIT PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Student Management System",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎓 Student Management System")

# =========================================================
# DATABASE CONNECTION (SAFE)
# =========================================================

@st.cache_resource
def get_connection():
    return sqlite3.connect("students.db", check_same_thread=False)

conn = get_connection()
cursor = conn.cursor()

# =========================================================
# CREATE TABLE (SAFE)
# =========================================================

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

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_active_students():
    cursor.execute("SELECT * FROM students WHERE status='ACTIVE'")
    return cursor.fetchall()

def dataframe_from_rows(rows):
    return pd.DataFrame(rows, columns=[
        "ID", "Name", "Email", "Phone",
        "Department", "Year", "Status",
        "Created At", "Updated At"
    ])

# =========================================================
# SIDEBAR MENU
# =========================================================

menu = [
    "Add Student",
    "View Students",
    "Search & Filter",
    "Update Student",
    "Deactivate Student"
]

choice = st.sidebar.selectbox("Menu", menu)

# =========================================================
# ADD STUDENT
# =========================================================

if choice == "Add Student":
    st.subheader("➕ Add Student")

    name = st.text_input("Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    department = st.selectbox("Department", ["CSE", "AIML", "DS", "ECE"])
    year = st.selectbox("Year", [1, 2, 3, 4])

    if st.button("Save Student"):
        if not name.strip() or not email.strip():
            st.warning("Name and Email are required")
        else:
            try:
                cursor.execute("""
                INSERT INTO students
                (name, email, phone, department, year, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (name, email, phone, department, year, now(), now()))
                conn.commit()
                st.success("Student added successfully")
            except sqlite3.IntegrityError:
                st.error("Email already exists")

# =========================================================
# VIEW STUDENTS
# =========================================================

elif choice == "View Students":
    st.subheader("📋 Active Students")

    rows = get_active_students()

    if rows:
        st.dataframe(dataframe_from_rows(rows), use_container_width=True)
    else:
        st.info("No students found")

# =========================================================
# SEARCH & FILTER (100% SAFE)
# =========================================================

elif choice == "Search & Filter":
    st.subheader("🔍 Search Students")

    keyword = st.text_input("Search by Name")
    dept = st.selectbox("Department", ["All", "CSE", "AIML", "DS", "ECE"])

    query = "SELECT * FROM students WHERE status='ACTIVE'"
    params = []

    if keyword.strip():
        query += " AND name LIKE ?"
        params.append(f"%{keyword}%")

    if dept != "All":
        query += " AND department=?"
        params.append(dept)

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()

    if rows:
        st.dataframe(dataframe_from_rows(rows), use_container_width=True)
    else:
        st.warning("No matching records")

# =========================================================
# UPDATE STUDENT
# =========================================================

elif choice == "Update Student":
    st.subheader("✏️ Update Student")

    rows = get_active_students()

    if not rows:
        st.info("No students available")
    else:
        ids = [r[0] for r in rows]
        student_id = st.selectbox("Select Student ID", ids)

        cursor.execute("SELECT * FROM students WHERE id=?", (student_id,))
        s = cursor.fetchone()

        name = st.text_input("Name", s[1])
        email = st.text_input("Email", s[2])
        phone = st.text_input("Phone", s[3])
        department = st.selectbox(
            "Department",
            ["CSE", "AIML", "DS", "ECE"],
            index=["CSE", "AIML", "DS", "ECE"].index(s[4])
        )
        year = st.selectbox("Year", [1, 2, 3, 4], index=s[5] - 1)

        if st.button("Update"):
            cursor.execute("""
            UPDATE students SET
            name=?, email=?, phone=?, department=?, year=?, updated_at=?
            WHERE id=?
            """, (name, email, phone, department, year, now(), student_id))
            conn.commit()
            st.success("Student updated successfully")

# =========================================================
# DEACTIVATE STUDENT (SOFT DELETE)
# =========================================================

elif choice == "Deactivate Student":
    st.subheader("🚫 Deactivate Student")

    rows = get_active_students()

    if not rows:
        st.info("No students available")
    else:
        ids = [r[0] for r in rows]
        student_id = st.selectbox("Select Student ID", ids)

        if st.button("Deactivate"):
            cursor.execute("""
            UPDATE students SET status='INACTIVE', updated_at=?
            WHERE id=?
            """, (now(), student_id))
            conn.commit()
            st.warning("Student deactivated")

# =========================================================
# END
# =========================================================
