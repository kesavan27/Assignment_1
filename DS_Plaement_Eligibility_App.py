# placement_app_mysql.py

import mysql.connector
from faker import Faker
import random
import streamlit as st
import pandas as pd

# ---------- Database Connection ----------


connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shanthi120$"
    )

query = "CREATE DATABASE IF NOT EXISTS placement_db"
cursor = connection.cursor()
cursor.execute(query)
cursor.close()

connection.commit()

# ---------- Data Models ----------


class Student:
    def __init__(self, faker):
        self.name = faker.name()
        self.age = random.randint(20, 25)
        self.gender = random.choice(['Male', 'Female', 'Other'])
        self.email = faker.email()
        self.phone = faker.phone_number()
        self.enrollment_year = random.randint(2019, 2022)
        self.course_batch = f"Batch-{random.randint(1,5)}"
        self.city = faker.city()
        self.graduation_year = self.enrollment_year + 4

class Programming:
    def __init__(self):
        self.language = random.choice(['Python', 'SQL'])
        self.problems_solved = random.randint(10, 200)
        self.assessments_completed = random.randint(1, 10)
        self.mini_projects = random.randint(0, 5)
        self.certifications_earned = random.randint(0, 3)
        self.latest_project_score = random.randint(50, 100)

class SoftSkill:
    def __init__(self):
        self.communication = random.randint(50, 100)
        self.teamwork = random.randint(50, 100)
        self.presentation = random.randint(50, 100)
        self.leadership = random.randint(50, 100)
        self.critical_thinking = random.randint(50, 100)
        self.interpersonal_skills = random.randint(50, 100)

class Placement:
    def __init__(self):
        self.mock_interview_score = random.randint(50, 100)
        self.internships_completed = random.randint(0, 3)
        self.placement_status = random.choice(['Ready', 'Not Ready', 'Placed'])
        self.company_name = random.choice(['TCS', 'Infosys', 'Google', 'Amazon', '']) if self.placement_status == 'Placed' else ''
        self.placement_package = random.randint(300000, 2000000) if self.placement_status == 'Placed' else 0
        self.interview_rounds_cleared = random.randint(0, 5)
        self.placement_date = faker.date_this_year() if self.placement_status == 'Placed' else None

# ---------- Database Setup ----------

def create_tables(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100), age INT, gender VARCHAR(10),
            email VARCHAR(100), phone VARCHAR(20),
            enrollment_year INT, course_batch VARCHAR(20),
            city VARCHAR(50), graduation_year INT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS programming (
            programming_id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT,
            language VARCHAR(20), problems_solved INT,
            assessments_completed INT, mini_projects INT,
            certifications_earned INT, latest_project_score INT,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS soft_skills (
            soft_skill_id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT,
            communication INT, teamwork INT, presentation INT,
            leadership INT, critical_thinking INT, interpersonal_skills INT,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS placements (
            placement_id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT,
            mock_interview_score INT, internships_completed INT,
            placement_status VARCHAR(20), company_name VARCHAR(50),
            placement_package INT, interview_rounds_cleared INT,
            placement_date DATE,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    """)

# ---------- Data Insertion ----------

def insert_data(conn, cursor, num_students=100):
    faker = Faker()
    for _ in range(num_students):
        student = Student(faker)
        cursor.execute("""
            INSERT INTO students (name, age, gender, email, phone,
            enrollment_year, course_batch, city, graduation_year)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (student.name, student.age, student.gender, student.email,
              student.phone, student.enrollment_year, student.course_batch,
              student.city, student.graduation_year))

        student_id = cursor.lastrowid

        programming = Programming()
        cursor.execute("""
            INSERT INTO programming (student_id, language, problems_solved,
            assessments_completed, mini_projects, certifications_earned, latest_project_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (student_id, programming.language, programming.problems_solved,
              programming.assessments_completed, programming.mini_projects,
              programming.certifications_earned, programming.latest_project_score))

        soft_skill = SoftSkill()
        cursor.execute("""
            INSERT INTO soft_skills (student_id, communication, teamwork, presentation,
            leadership, critical_thinking, interpersonal_skills)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (student_id, soft_skill.communication, soft_skill.teamwork,
              soft_skill.presentation, soft_skill.leadership,
              soft_skill.critical_thinking, soft_skill.interpersonal_skills))

        placement = Placement()
        cursor.execute("""
            INSERT INTO placements (student_id, mock_interview_score,
            internships_completed, placement_status, company_name,
            placement_package, interview_rounds_cleared, placement_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (student_id, placement.mock_interview_score,
              placement.internships_completed, placement.placement_status,
              placement.company_name, placement.placement_package,
              placement.interview_rounds_cleared, placement.placement_date))

    conn.commit()

# ---------- Streamlit UI ----------

def streamlit_ui():
    st.title("Placement Eligibility App")
    st.sidebar.header("Filter Criteria")
    
    min_problems = st.sidebar.slider("Min Problems Solved", 0, 200, 50)
    min_soft_skills = st.sidebar.slider("Min Avg Soft Skills Score", 0, 100, 75)
    status = st.sidebar.selectbox("Placement Status", ["Ready", "Not Ready", "Placed"])

    conn = connect_db()
    query = f"""
        SELECT s.name, s.email, s.course_batch, p.problems_solved,
               (ss.communication + ss.teamwork + ss.presentation +
                ss.leadership + ss.critical_thinking + ss.interpersonal_skills)/6 AS avg_soft_skills,
               pl.placement_status, pl.company_name, pl.placement_package
        FROM students s
        JOIN programming p ON s.student_id = p.student_id
        JOIN soft_skills ss ON s.student_id = ss.student_id
        JOIN placements pl ON s.student_id = pl.student_id
        WHERE p.problems_solved >= {min_problems}
        AND pl.placement_status = '{status}'
        HAVING avg_soft_skills >= {min_soft_skills}
    """
    df = pd.read_sql(query, conn)
    st.dataframe(df)

# ---------- Main ----------

if __name__ == '__main__':
    faker = Faker()
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shanthi120$",
        database="placement_db"
    )
    cursor = conn.cursor()
    create_tables(cursor)
    insert_data(conn, cursor, num_students=100)
    cursor.close()
    conn.close()
    streamlit_ui()

# ---------- SQL Queries for Insights (to be saved in SQL or displayed in app) ----------
# 1. Average problems solved per batch
# 2. Top 5 students with highest mock interview score
# 3. Avg soft skills score per student
# 4. Students placed and their packages
# 5. Number of students placed per company
# 6. Students with more than 1 internship
# 7. Avg project score by language
# 8. Students who cleared more than 3 interview rounds
# 9. Placement status distribution
# 10. Avg placement package per batch
