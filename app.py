import streamlit as st
import sqlite3
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Employee Management System",
    page_icon="💼",
    layout="wide"
)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("employees.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    phone TEXT,
    department TEXT,
    experience INTEGER,
    salary INTEGER
)
""")
conn.commit()

# ---------------- TITLE ----------------
st.title("💼 Employee Management System")

menu = [
    "📊 Dashboard",
    "➕ Add Employee",
    "📋 View Employees",
    "✏️ Update Employee",
    "🗑️ Delete Employee"
]
choice = st.sidebar.selectbox("📌 Navigation", menu)

# ---------------- DASHBOARD ----------------
if choice == "📊 Dashboard":
    st.header("📊 Employee Dashboard")

    df = pd.read_sql("SELECT * FROM employees", conn)

    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("👥 Total Employees", len(df))
        col2.metric("💰 Average Salary", f"₹ {int(df['salary'].mean())}")
        col3.metric("🏢 Departments", df['department'].nunique())
        col4.metric("🕒 Avg Experience (Years)", round(df['experience'].mean(), 1))

        st.subheader("Employees by Department")
        dept_count = df['department'].value_counts()
        st.bar_chart(dept_count)

        st.subheader("Salary Distribution")
        st.bar_chart(df['salary'])
    else:
        st.info("No employee data available")

# ---------------- ADD EMPLOYEE ----------------
elif choice == "➕ Add Employee":
    st.header("Add New Employee")

    col1, col2, col3 = st.columns(3)

    with col1:
        name = st.text_input("Name")
        email = st.text_input("Email")

    with col2:
        phone = st.text_input("Phone")
        department = st.selectbox(
            "Department", ["HR", "IT", "Finance", "Sales", "Operations"]
        )

    with col3:
        experience = st.number_input("Experience (Years)", min_value=0, max_value=40)
        salary = st.number_input("Salary (₹)", min_value=0)

    if st.button("Save Employee"):
        if name and email and phone:
            cursor.execute("""
                INSERT INTO employees
                (name, email, phone, department, experience, salary)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, email, phone, department, experience, salary))
            conn.commit()

            st.success("✅ Employee added successfully")
        else:
            st.error("❌ Please fill all required fields")

# ---------------- VIEW EMPLOYEES ----------------
elif choice == "📋 View Employees":
    st.header("Employee Records")

    df = pd.read_sql("SELECT * FROM employees", conn)
    st.dataframe(df, use_container_width=True)

# ---------------- UPDATE EMPLOYEE ----------------
elif choice == "✏️ Update Employee":
    st.header("Update Employee Details")

    employee_ids = pd.read_sql("SELECT id FROM employees", conn)["id"].tolist()

    if employee_ids:
        selected_id = st.selectbox("Select Employee ID", employee_ids)
        emp = cursor.execute(
            "SELECT * FROM employees WHERE id=?", (selected_id,)
        ).fetchone()

        col1, col2, col3 = st.columns(3)

        with col1:
            name = st.text_input("Name", emp[1])
            email = st.text_input("Email", emp[2])

        with col2:
            phone = st.text_input("Phone", emp[3])
            department = st.selectbox(
                "Department",
                ["HR", "IT", "Finance", "Sales", "Operations"],
                index=["HR", "IT", "Finance", "Sales", "Operations"].index(emp[4])
            )

        with col3:
            experience = st.number_input("Experience (Years)", value=emp[5])
            salary = st.number_input("Salary (₹)", value=emp[6])

        if st.button("Update Employee"):
            cursor.execute("""
                UPDATE employees
                SET name=?, email=?, phone=?, department=?, experience=?, salary=?
                WHERE id=?
            """, (name, email, phone, department, experience, salary, selected_id))
            conn.commit()
            st.success("🎉 Employee updated successfully")
    else:
        st.info("No employees found")

# ---------------- DELETE EMPLOYEE ----------------
elif choice == "🗑️ Delete Employee":
    st.header("Delete Employee")

    employee_ids = pd.read_sql("SELECT id FROM employees", conn)["id"].tolist()

    if employee_ids:
        selected_id = st.selectbox("Select Employee ID", employee_ids)

        if st.button("Delete Employee"):
            cursor.execute("DELETE FROM employees WHERE id=?", (selected_id,))
            conn.commit()
            st.warning("⚠️ Employee deleted successfully")
    else:
        st.info("No employees available")
