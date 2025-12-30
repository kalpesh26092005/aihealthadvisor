import mysql.connector
from mysql.connector import Error
import hashlib
import json
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', 'kalpesh2005?')
        self.database = os.getenv('DB_NAME', 'ai_health_advisor')

    def get_connection(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return connection
        except Error as e:
            print("DATABASE CONNECTION ERROR:", e)
            return None

    # --------------------------
    # Create users table
    # --------------------------
    def create_tables(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_name VARCHAR(100) NOT NULL,
                    contact_number VARCHAR(20) NOT NULL,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            cursor.close()
            conn.close()
            print("Tables created successfully.")
        except Error as e:
            print("TABLE CREATION ERROR:", e)

    # --------------------------
    # Register User - FIXED INDENTATION
    # --------------------------
    def register_user(self, user_name, contact_number, email, password):
        print(f"\n=== DATABASE REGISTRATION ATTEMPT ===")
        print(f"Username: {user_name}")
        print(f"Contact: {contact_number}")
        print(f"Email: {email}")
        print(f"Password length: {len(password)}")
        
        try:
            conn = self.get_connection()
            if conn is None:
                print("ERROR: Database connection is None")
                return {"success": False, "message": "Database connection failed"}

            print("✓ Database connection established")
            
            cursor = conn.cursor()

            # Check if email already registered
            print(f"Checking if email '{email}' exists...")
            cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
            existing = cursor.fetchone()

            if existing:
                print(f"✗ Email '{email}' already exists in database")
                cursor.close()
                conn.close()
                return {"success": False, "message": "Email already registered"}

            print("✓ Email is not registered yet")

            # Hash password
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            print(f"Password hash: {password_hash[:20]}...")

            # Insert user
            query = """
                INSERT INTO users (user_name, contact_number, email, password_hash)
                VALUES (%s, %s, %s, %s)
            """
            
            print("Executing insert query...")
            cursor.execute(query, (user_name, contact_number, email, password_hash))
            conn.commit()
            
            # Get the inserted user ID
            user_id = cursor.lastrowid
            print(f"✓ User inserted successfully! User ID: {user_id}")

            cursor.close()
            conn.close()
            print("✓ Database connection closed")

            return {
                "success": True, 
                "message": "Registration successful",
                "user_id": user_id
            }

        except mysql.connector.Error as e:
            print(f"\n✗ MySQL ERROR: {e}")
            print(f"Error code: {e.errno}")
            print(f"SQL State: {e.sqlstate}")
            
            # More specific error messages
            if e.errno == 1062:  # Duplicate entry error code
                return {"success": False, "message": "Email already registered"}
            elif e.errno == 1045:  # Access denied
                return {"success": False, "message": "Database access denied"}
            elif e.errno == 1049:  # Unknown database
                return {"success": False, "message": "Database does not exist"}
            elif e.errno == 2003:  # Can't connect to MySQL server
                return {"success": False, "message": "Cannot connect to database server"}
            else:
                return {"success": False, "message": f"Database error: {e}"}
        except Exception as e:
            print(f"\n✗ UNEXPECTED ERROR: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "message": "Registration failed due to system error"}

    # --------------------------
    # Login
    # --------------------------
    def check_login(self, email, password):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            password_hash = hashlib.sha256(password.encode()).hexdigest()

            cursor.execute("""
                SELECT * FROM users WHERE email=%s AND password_hash=%s
            """, (email, password_hash))

            user = cursor.fetchone()

            cursor.close()
            conn.close()

            return user

        except Error as e:
            print("LOGIN ERROR:", e)
            return None
        

    def create_tables(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

        # Users table (already exists)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_name VARCHAR(100) NOT NULL,
                    contact_number VARCHAR(20) NOT NULL,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

        # Add these new tables:
        
        # Symptom history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS symptoms_history (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT NOT NULL,
                    symptoms TEXT NOT NULL,
                    analysis_result TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

        # AI consultations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_consultations (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT NOT NULL,
                    question TEXT NOT NULL,
                    response TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

        # Medicine reminders table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS medicine_reminders (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT NOT NULL,
                    medicine_name VARCHAR(100) NOT NULL,
                    dosage VARCHAR(50),
                    schedule VARCHAR(100),
                    reminder_time TIME,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            conn.commit()
            cursor.close()
            conn.close()
            print("Tables created successfully.")
        except Error as e:
            print("TABLE CREATION ERROR:", e)
            
    def get_user_stats(self, user_id):
        """Get statistics for a specific user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
        
            # Get symptom check count
            cursor.execute("""
                SELECT COUNT(*) as symptom_checks 
                FROM symptoms_history 
                WHERE user_id = %s
            """, (user_id,))
            symptom_result = cursor.fetchone()
            symptom_checks = symptom_result['symptom_checks'] if symptom_result else 0
        
            # Get AI consultations count
            cursor.execute("""
                SELECT COUNT(*) as ai_consultations 
                FROM ai_consultations 
                WHERE user_id = %s
         """, (user_id,))
            ai_result = cursor.fetchone()
            ai_consultations = ai_result['ai_consultations'] if ai_result else 0
        
            # Get active reminders count
            cursor.execute("""
                SELECT COUNT(*) as active_reminders 
                FROM medicine_reminders 
                WHERE user_id = %s AND is_active = TRUE
            """, (user_id,))
            reminders_result = cursor.fetchone()
            active_reminders = reminders_result['active_reminders'] if reminders_result else 0
        
            # Calculate health score (simplified version)
            # You can make this more sophisticated
            health_score = min(85 + (symptom_checks * 2), 100)
        
            cursor.close()
            conn.close()
        
            return {
                'symptom_checks': symptom_checks,
                'ai_consultations': ai_consultations,
                'active_reminders': active_reminders,
                'health_score': health_score
         }
        
        except Error as e:
            print("GET USER STATS ERROR:", e)
        return {
                'symptom_checks': 0,
                'ai_consultations': 0,
                'active_reminders': 0,
                'health_score': 85
            }

    def add_symptom_check(self, user_id, symptoms, analysis_result=None):
        """Add a new symptom check to history"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            if isinstance(analysis_result, dict):
                analysis_json = json.dumps(analysis_result)
            else:
                analysis_json = str(analysis_result)
        
            cursor.execute("""
             INSERT INTO symptom_history (user_id, symptoms, analysis_result, created_at) 
            VALUES (%s, %s, %s, NOW())
        """, (user_id, symptoms, analysis_json))
        
            conn.commit()
            cursor.close()
            conn.close()
        
            return {"success": True, "message": "Symptom check recorded"}
        
        except Error as e:
            print("ADD SYMPTOM CHECK ERROR:", e)
            return {"success": False, "message": str(e)}

    def add_ai_consultation(self, user_id, question, response):
        """Add an AI consultation to history"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
        
            cursor.execute("""
                INSERT INTO ai_consultations (user_id, question, response)
                VALUES (%s, %s, %s)
            """, (user_id, question, response))
        
            conn.commit()
            cursor.close()
            conn.close()
        
            return {"success": True, "message": "AI consultation recorded"}
        
        except Error as e:
            print("ADD AI CONSULTATION ERROR:", e)
            return {"success": False, "message": str(e)}            
    