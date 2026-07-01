import csv
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

db_host = os.environ.get("DB_HOST", "localhost")
db_user = os.environ.get("DB_USER", "root")
db_password = os.environ.get("DB_PASSWORD", "")
db_database = os.environ.get("DB_DATABASE", "school_db")

con = mysql.connect(
    user=db_user,
    host=db_host,
    password=db_password,
    database=db_database
)
cur = con.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS class_timetable(
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
                PRIMARY KEY (class_section, day));""")
cur.execute("""CREATE TABLE IF NOT EXISTS teacher_timetable(
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
                PRIMARY KEY (teacher, day));""")


f = open("School_Schedule.csv","r")
read = csv.reader(f)
csvdata = []
for i in read:
    csvdata.append(i)

def schedule_timetable(data, days, periods):
    classes = []
    timetable = {}
    for i in range(1,len(data)):
        x = data[i][0] + "-" + data[i][1]
        if x not in classes:
            classes.append(x)
    
    for cls in classes:
        subjects = []
        teachers = []
        rows = {}
        for i in range(1,len(data)):
            if data[i][0] + "-" + data[i][1] == cls:
                subjects.append(data[i][2])
                teachers.append(data[i][3])
        
        for day in days:
            periodlst = []
            for period in range(periods):
                index = random.randint(0,len(subjects)-1)
                subject = subjects[index]
                teacher = teachers[index]
                subject_teach = (subject,teacher)
                periodlst.append(subject_teach)
            rows.update({day:periodlst})
        timetable[cls] = rows
                
    return timetable

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
    return teacher_timetable
        
def save_class_timetable_to_mysql(connection, timetable):
    with connection.cursor() as cursor:
        for cls, days in timetable.items():
            for day, periods in days.items():
                formatted_periods = []
                for period in periods:
                    if period is None:  
                        formatted_periods.append(None)
                    else:  
                        subject, teacher = period
                        formatted_periods.append(f"{subject} ({teacher})")

                cursor.execute("""
                    INSERT INTO class_timetable (class_section, day, period_1, period_2, period_3, period_4, period_5, period_6, period_7, period_8, period_9)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    period_1 = VALUES(period_1), period_2 = VALUES(period_2), period_3 = VALUES(period_3),
                    period_4 = VALUES(period_4), period_5 = VALUES(period_5), period_6 = VALUES(period_6),
                    period_7 = VALUES(period_7), period_8 = VALUES(period_8), period_9 = VALUES(period_9);
                """, (cls, day, *formatted_periods))
    connection.commit()

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

time_table =    schedule_timetable(csvdata, ["1Monday","2Tuesday","3Wednesday","4Thursday","5Friday"],9)
teacher_time_table = generate_teacher_timetable(time_table)
save_class_timetable_to_mysql(con, time_table)
save_teacher_timetable_to_mysql(con, teacher_time_table)
print("Time table saved to SQL!")
con.close()
f.close()
