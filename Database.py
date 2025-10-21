import pymysql

DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = ""
DB_NAME = "payright_payroll"


def get_connection():
    """Establish MySQL connection."""
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )


def create_database_and_tables():
    """Create database and all required tables."""
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = connection.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    cursor.execute(f"USE {DB_NAME}")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(100) NOT NULL,
        role ENUM('admin','employee') DEFAULT 'employee'
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50),
        name VARCHAR(100),
        position VARCHAR(100),
        department VARCHAR(100),
        salary DECIMAL(10,2)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pending_employees (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50),
        password VARCHAR(100),
        name VARCHAR(100),
        position VARCHAR(100),
        department VARCHAR(100),
        salary DECIMAL(10,2),
        status ENUM('pending','accepted') DEFAULT 'pending'
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payroll (
        id INT AUTO_INCREMENT PRIMARY KEY,
        employee_name VARCHAR(100),
        position VARCHAR(100),
        base DECIMAL(10,2),
        overtime DECIMAL(10,2),
        allowance DECIMAL(10,2),
        deductions DECIMAL(10,2),
        netpay DECIMAL(10,2),
        date_issued DATE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INT AUTO_INCREMENT PRIMARY KEY,
        employee_name VARCHAR(100),
        time_in DATETIME,
        time_out DATETIME
    );
    """)

    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username,password,role) VALUES (%s,%s,%s)",
            ("admin", "1234", "admin")
        )
        connection.commit()
        print("✅ Default admin created (admin / 1234)")

    connection.commit()
    connection.close()


def verify_user(username, password):
    """Return user role if login valid, else None."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT role FROM users WHERE username=%s AND password=%s", (username, password))
        user = cur.fetchone()
        conn.close()
        return user["role"] if user else None
    except Exception as e:
        print("DB Error:", e)
        return None


def register_pending_employee(username, password, name, position, department, salary):
    """Add new employee request for approval."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO pending_employees (username,password,name,position,department,salary)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (username, password, name, position, department, salary))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("❌ Error adding pending employee:", e)
        return False


def fetch_pending_employees():
    """Return list of pending employees."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT username, name, position, department, salary FROM pending_employees WHERE status='pending'")
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print("❌ Error fetching pending:", e)
        return []


def approve_employee(username):
    """Approve a pending employee and create an account."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM pending_employees WHERE username=%s", (username,))
        emp = cur.fetchone()
        if not emp:
            return False

        cur.execute("""
            INSERT INTO users (username,password,role) VALUES (%s,%s,%s)
        """, (emp["username"], emp["password"], "employee"))
        cur.execute("""
            INSERT INTO employees (username, name, position, department, salary)
            VALUES (%s, %s, %s, %s, %s)
        """, (emp["username"], emp["name"], emp["position"], emp["department"], emp["salary"]))
        cur.execute("DELETE FROM pending_employees WHERE username=%s", (username,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("❌ Error approving:", e)
        return False


def reject_employee(username):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM pending_employees WHERE username=%s", (username,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("❌ Error rejecting employee:", e)
        return False


def is_employee_approved(username):
    """Check if the employee account is approved."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM employees WHERE username=%s", (username,))
        emp = cur.fetchone()
        conn.close()
        return bool(emp)
    except Exception as e:
        print("❌ Error checking approval:", e)
        return False
