# StructDB - A Data Structures-Based Mini Database Engine

**Group 40 - BCA Project**  
**Graphic Era Hill University, Bhimtal, Uttarakhand**

## Team Members
- **Pooja Padiyar** - University Roll No: 2471382
- **Kavyanka Joshi** - University Roll No: 2471107
- **Harshit Dhaila** - University Roll No: 2471073
- **Piyush Jeena** - University Roll No: 2471381

**Supervisor:** Mrs. Divya Rastogi

---

## 📋 Project Overview

StructDB is a lightweight, educational mini database engine built with Python and Tkinter. It combines traditional database operations with an intuitive GUI and SQL-like query language, making database concepts accessible while providing practical functionality.

## ✨ Key Features

### 🔐 Authentication & User Management
- User registration and login
- SHA-256 password hashing
- Role-based access control (admin/user)
- Session management
- Default admin account (username: `admin`, password: `admin123`)

### 💾 Multi-Database Support
- Each user can create multiple databases
- Optional password protection per database
- Database isolation per user
- CREATE, USE, DROP database commands

### 📊 Complete SQL-Like Query Language
- **Database Operations:** CREATE DATABASE, DROP DATABASE, USE, SHOW DATABASES
- **Table Operations:** CREATE TABLE, DROP TABLE, SHOW TABLES
- **CRUD Operations:** INSERT, SELECT, UPDATE, DELETE
- **Advanced Queries:** WHERE, ORDER BY, LIMIT
- **Aggregate Functions:** COUNT, SUM, AVG, MIN, MAX
- **Operators:** =, !=, >, <, >=, <=, AND

### 🎨 Modern GUI (Tkinter)
- **Three-Tab Interface:**
  - **GUI Mode:** Form-based CRUD operations
  - **Query Mode:** SQL query editor with examples
  - **Database Info:** Statistics and information
- Database Manager for easy database creation/switching
- TreeView for displaying records
- Dynamic form generation based on table structure
- Export to CSV functionality

### 🔧 Data Structures & Algorithms
- **Hash Table:** O(1) primary key indexing with collision handling
- **Linked List:** For collision resolution (chaining method)
- **Dynamic Arrays:** For efficient record storage
- JSON-based persistent storage

### 📈 Additional Features
- Query history tracking
- Automatic timestamps (_created_at, _updated_at)
- Primary key validation
- Duplicate prevention
- Type inference and conversion
- Comprehensive error handling

---

## 📁 Project Structure

```
StructDB/
│
├── main.py                 # Main entry point
├── gui.py                  # Tkinter GUI application
├── database_manager.py     # Multi-database manager
├── database.py             # Database engine with CRUD operations
├── query_parser.py         # SQL-like query parser
├── data_structures.py      # Hash table & linked list implementation
├── README.md               # This file
│
└── structdb_data/          # Data directory (auto-created)
    ├── users.json          # User accounts
    └── *.json              # Database files
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Tkinter (usually included with Python)

### Installation Steps

1. **Clone or download the project:**
   ```bash
   git clone <repository-url>
   cd StructDB
   ```

2. **Verify Python installation:**
   ```bash
   python --version
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

---

## 📖 Usage Guide

### 1. First Login
- **Username:** `admin`
- **Password:** `admin123`

### 2. Register New User (Optional)
- Click "Register" on login screen
- Enter username and password
- Confirm password
- Click "Register"

### 3. Create Your First Database
1. Click "Manage Databases" button
2. Enter database name (e.g., "school")
3. Optionally add password for security
4. Click "Create"

### 4. Use a Database
1. In Database Manager, select database from dropdown
2. Enter password if protected
3. Click "Use"

### 5. Create Tables (Query Mode)
```sql
CREATE TABLE students (id, name, age, grade)
```

### 6. Insert Data
**GUI Mode:**
- Fill the form with data
- Click "Insert"

**Query Mode:**
```sql
INSERT INTO students VALUES (1, 'John Doe', 20, 'A')
INSERT INTO students VALUES (2, 'Jane Smith', 19, 'B')
```

### 7. Query Data
```sql
-- Select all records
SELECT * FROM students

-- Filter with WHERE
SELECT * FROM students WHERE age > 18

-- Order and limit results
SELECT * FROM students WHERE grade = 'A' ORDER BY name LIMIT 10

-- Aggregate functions
SELECT COUNT(*) FROM students
SELECT AVG(age) FROM students WHERE grade = 'A'
```

### 8. Update Records
```sql
UPDATE students SET grade = 'A+' WHERE id = 1
```

### 9. Delete Records
```sql
DELETE FROM students WHERE age < 18
```

### 10. Export Data
- Select table in GUI Mode
- Click "Export CSV"
- File saved with timestamp

---

## 🔍 SQL Query Examples

### Database Management
```sql
-- Create a new database
CREATE DATABASE myschool

-- Switch to database
USE myschool

-- List all databases
SHOW DATABASES

-- Drop database
DROP DATABASE myschool
```

### Table Management
```sql
-- Create table
CREATE TABLE employees (emp_id, name, department, salary)

-- List all tables
SHOW TABLES

-- Drop table
DROP TABLE employees
```

### CRUD Operations
```sql
-- Insert records
INSERT INTO employees VALUES (101, 'Alice Johnson', 'IT', 75000)
INSERT INTO employees VALUES (102, 'Bob Williams', 'HR', 65000)

-- Select queries
SELECT * FROM employees
SELECT * FROM employees WHERE salary > 70000
SELECT * FROM employees WHERE department = 'IT' ORDER BY name
SELECT * FROM employees WHERE salary >= 60000 ORDER BY salary DESC LIMIT 5

-- Update records
UPDATE employees SET salary = 80000 WHERE emp_id = 101

-- Delete records
DELETE FROM employees WHERE salary < 50000
```

### Aggregate Functions
```sql
-- Count records
SELECT COUNT(*) FROM employees

-- Average salary
SELECT AVG(salary) FROM employees

-- Sum of salaries
SELECT SUM(salary) FROM employees WHERE department = 'IT'

-- Min and Max
SELECT MIN(salary) FROM employees
SELECT MAX(salary) FROM employees
```

---

## 🏗️ Architecture

### System Components

1. **Presentation Layer (gui.py)**
   - User interface components
   - Form validation and input handling
   - Result display and error messaging

2. **Business Logic Layer (database_manager.py)**
   - Query processing and parsing
   - Data validation and business rules
   - Authentication and authorization

3. **Data Layer (database.py)**
   - File-based persistent storage
   - In-memory data structures
   - Indexing and searching algorithms

4. **Query Processing (query_parser.py)**
   - SQL-like query parsing
   - Syntax validation
   - Command extraction

5. **Data Structures (data_structures.py)**
   - Hash table implementation
   - Linked list for collision handling

### Data Flow
```
User Input → GUI → Database Manager → Query Parser → Database Engine → Data Structures → Storage
```

---

## 🔒 Security Features

- **Password Hashing:** SHA-256 encryption for all passwords
- **Database Protection:** Optional password per database
- **User Isolation:** Each user has separate databases
- **Session Management:** Secure login/logout functionality
- **Input Validation:** Prevents SQL injection-like attacks

---

## 📊 Performance Characteristics

- **Hash Table Indexing:** O(1) average-case lookup time
- **Record Insertion:** O(1) average-case
- **Record Search:** O(1) with primary key, O(n) with conditions
- **Record Update/Delete:** O(n) for finding + O(1) for operation
- **Supports:** 1000+ records with acceptable performance
- **Response Time:** Sub-second for most operations

---

## 🎓 Educational Value

This project demonstrates:
- Data structures implementation (Hash Tables, Linked Lists)
- Algorithm design and analysis
- Database concepts (CRUD, indexing, querying)
- GUI development with Tkinter
- File I/O and data persistence
- Authentication systems
- Query language parsing
- Software architecture and modularity

---

## 🐛 Known Limitations

1. In-memory operations (limited by RAM)
2. No concurrent user support
3. No transaction support
4. No foreign key constraints
5. No JOIN operations
6. Basic query optimization
7. Limited to single-machine deployment

---

## 🔮 Future Enhancements

- [ ] JOIN operations support
- [ ] Transaction management (COMMIT, ROLLBACK)
- [ ] Foreign key constraints
- [ ] Indexing on non-primary key columns
- [ ] Query optimization
- [ ] Import from CSV/Excel
- [ ] Database backup and restore
- [ ] User permission system
- [ ] Dark mode UI
- [ ] Network access (client-server)

---

## 📝 License

This project is created for educational purposes as part of the BCA curriculum at Graphic Era Hill University, Bhimtal.

---

## 👥 Support & Contact

For issues or questions regarding this project, please contact the team members through the university.

**Institution:** Graphic Era Hill University, Bhimtal, Uttarakhand  
**School:** School of Computing  
**Project Group:** 40

---

## 🙏 Acknowledgments

- Mrs. Divya Rastogi (Project Supervisor)
- Graphic Era Hill University, Bhimtal
- School of Computing Faculty

---

**© 2024 StructDB - Group 40 | Graphic Era Hill University**