# SchedulEaze (Time Table Scheduler)

A Python-based scheduling application that reads school schedules from CSV datasets, processes them using randomized scheduling algorithms to avoid teacher double-booking, and exports the final class and teacher timetables to a MySQL database.

---

## How to Set Up and Demo on a New System

Follow these steps to configure and run this project on a fresh machine:

### Prerequisites
Make sure the new system has the following installed:
1. **Python 3.x**
2. **MySQL Server** (and optionally a database viewer like MySQL Workbench, DBeaver, or phpMyAdmin)

---

### Step-by-Step Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/madhusudhan-muppi/SchedulEaze.git
cd SchedulEaze
```

#### 2. Set Up the MySQL Database
Log into your MySQL terminal:
```bash
mysql -u root -p
```
Run the following SQL query to create the database:
```sql
CREATE DATABASE school_db;
```

#### 3. Configure the Environment File
Copy the example environment configuration:
```bash
cp .env.example .env
```
Open the newly created `.env` file and update it with your MySQL password and details:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_actual_password_here
DB_DATABASE=school_db
```

#### 4. Install Dependencies
Install the required Python packages:
```bash
pip install mysql-connector-python pandas
```

#### 5. Run the Scheduler
Run the primary script:
```bash
python "Time Table Scheduler.py"
```
Or run the pandas-based alternative:
```bash
python Test.py
```
*(If successful, you will see a console output: `Time table saved to SQL!`)*

---

### Verifying the Output (The Demo)

To show that the scheduling database was successfully populated, run these queries in your MySQL console:

```sql
USE school_db;

-- View class timetable
SELECT * FROM class_timetable LIMIT 10;

-- View teacher timetable
SELECT * FROM teacher_timetable LIMIT 10;
```
