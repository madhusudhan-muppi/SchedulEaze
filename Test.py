import pandas as pd
import random
import os
import mysql.connector as mysql

# Load environment variables from .env file if it exists
if os.path.exists(".env"):
    with open(".env") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip()

# MySQL connection details
MYSQL_HOST = os.environ.get("DB_HOST", "localhost")
MYSQL_USER = os.environ.get("DB_USER", "root")
MYSQL_PASSWORD = os.environ.get("DB_PASSWORD", "")
MYSQL_DATABASE = os.environ.get("DB_DATABASE", "school_db")

# Function to connect to MySQL
def connect_to_mysql():
    return mysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
    )

# Function to create tables in MySQL
def create_tables(connection):
    with connection.cursor() as cursor:
        # Create class timetable table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS class_timetable (
                class_section VARCHAR(50),
                day VARCHAR(20),
                period_1 VARCHAR(100),
                period_2 VARCHAR(100),
                period_3 VARCHAR(100),
                period_4 VARCHAR(100),
                period_5 VARCHAR(100),
                period_6 VARCHAR(100),
                period_7 VARCHAR(100),
                period_8 VARCHAR(100),
                period_9 VARCHAR(100),
                PRIMARY KEY (class_section, day)
            );
        """)
        # Create teacher timetable table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teacher_timetable (
                teacher VARCHAR(50),
                day VARCHAR(20),
                period_1 VARCHAR(100),
                period_2 VARCHAR(100),
                period_3 VARCHAR(100),
                period_4 VARCHAR(100),
                period_5 VARCHAR(100),
                period_6 VARCHAR(100),
                period_7 VARCHAR(100),
                period_8 VARCHAR(100),
                period_9 VARCHAR(100),
                PRIMARY KEY (teacher, day)
            );
        """)
    connection.commit()

# Function to save class timetable to MySQL
def save_class_timetable_to_mysql(connection, timetable):
    with connection.cursor() as cursor:
        for cls, days in timetable.items():
            for day, periods in days.items():
                # Safely handle None values
                formatted_periods = []
                for period in periods:
                    if period is None:  # If the period is not scheduled
                        formatted_periods.append(None)
                    else:  # Period contains (subject, teacher)
                        subject, teacher = period
                        formatted_periods.append(f"{subject} ({teacher})")

                # Insert the data into the database
                cursor.execute("""
                    INSERT INTO class_timetable (class_section, day, period_1, period_2, period_3, period_4, period_5, period_6, period_7, period_8, period_9)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    period_1 = VALUES(period_1), period_2 = VALUES(period_2), period_3 = VALUES(period_3),
                    period_4 = VALUES(period_4), period_5 = VALUES(period_5), period_6 = VALUES(period_6),
                    period_7 = VALUES(period_7), period_8 = VALUES(period_8), period_9 = VALUES(period_9);
                """, (cls, day, *formatted_periods))
    connection.commit()


# Function to generate a teacher timetable from class timetable
def generate_teacher_timetable(timetable):
    teacher_timetable = {}
    for cls, days in timetable.items():
        for day, periods in days.items():
            for period_idx, entry in enumerate(periods):
                if entry:  # If a subject and teacher is scheduled
                    subject, teacher = entry
                    if teacher not in teacher_timetable:
                        teacher_timetable[teacher] = {day: [None] * 9 for day in days}
                    teacher_timetable[teacher][day][period_idx] = f"{subject} ({cls})"
    print(teacher_timetable)

# Function to save teacher timetable to MySQL
def save_teacher_timetable_to_mysql(connection, timetable):
    with connection.cursor() as cursor:
        for teacher, days in timetable.items():
            for day, periods in days.items():
                cursor.execute("""
                    INSERT INTO teacher_timetable (teacher, day, period_1, period_2, period_3, period_4, period_5, period_6, period_7, period_8, period_9)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    period_1 = VALUES(period_1), period_2 = VALUES(period_2), period_3 = VALUES(period_3),
                    period_4 = VALUES(period_4), period_5 = VALUES(period_5), period_6 = VALUES(period_6),
                    period_7 = VALUES(period_7), period_8 = VALUES(period_8), period_9 = VALUES(period_9);
                """, (teacher, day, *[period if period else None for period in periods]))
    connection.commit()

# Read the input CSV file (Assumed columns: Class, Section, Subject, Teacher)
def load_data(file_path):
    return pd.read_csv(file_path)

# Initialize timetable dictionary
def initialize_timetable(classes, days, periods):
    timetable = {}
    for cls in classes:
        timetable[cls] = {day: [None] * periods for day in days}
    return timetable

# Function to check if a teacher is free for a given period and day
def is_teacher_free(timetable, teacher, day, period):
    for cls in timetable.values():
        if cls[day][period] and cls[day][period][1] == teacher:
            return False
    return True

# Function to schedule the timetable allowing subject repetition
def schedule_timetable(data, days, periods):
    classes = (data['Class'] + "-" + data['Section']).unique()
    timetable = initialize_timetable(classes, days, periods)

    for cls in classes:
        cls_data = data[(data['Class'] + "-" + data['Section']) == cls]
        subjects = cls_data['Subject'].tolist()
        teachers = cls_data['Teacher'].tolist()

        for day in days:
            for period in range(periods):
                # Randomly select a subject and teacher for the period
                index = random.randint(0, len(subjects) - 1)
                subject = subjects[index]
                teacher = teachers[index]

                # Ensure the teacher is not double-booked in the same period
                if timetable[cls][day][period] is None:
                    timetable[cls][day][period] = (subject, teacher)

    return timetable

# Main program
if __name__ == "__main__":
    file_path = "school_schedule.csv"  # Path to your CSV file
    data = load_data(file_path)
    days = ["1Monday", "2Tuesday", "3Wednesday", "4Thursday", "5Friday"]
    periods = 9

    # Generate the class timetable
    class_timetable = schedule_timetable(data, days, periods)

    # Generate the teacher timetable
    teacher_timetable = generate_teacher_timetable(class_timetable)

    # Connect to MySQL and save the timetables
    connection = connect_to_mysql()
    try:
        create_tables(connection)
        save_class_timetable_to_mysql(connection, class_timetable)
        save_teacher_timetable_to_mysql(connection, teacher_timetable)
        print("Timetables successfully saved to MySQL!")
    finally:
        connection.close()
