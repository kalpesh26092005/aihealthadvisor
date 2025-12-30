import os
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import traceback
from flask_cors import CORS
from database import Database
from flask import session, redirect, url_for
import mysql.connector
from mysql.connector import Error
from mysql.connector import pooling
from database import Database
import json
import re
import hashlib
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)


db = Database()

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://127.0.0.1:5000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/register')
def register():
    return render_template("registration.html")

@app.route('/symptoms')
def symptoms():
    return render_template('symptoms.html')

@app.route('/dashboard')
def dashboard():
    print(f"\n=== DASHBOARD ACCESS ATTEMPT ===")
    print(f"Session data: {dict(session)}")
    print(f"User ID in session: {session.get('user_id')}")
    
    if 'user_id' not in session:
        print("REDIRECT: No user_id in session, redirecting to login")
        return redirect(url_for('login'))
    
    print(f"ACCESS GRANTED: User {session.get('user_name')} accessing dashboard")
    return render_template('dashboard.html', user_name=session.get('user_name'))

@app.route('/contact')
def contact():
    return render_template('contact.html')




# Load API key from environment variables for security
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise EnvironmentError("Please set the GOOGLE_API_KEY environment variable")

genai.configure(api_key=api_key)

# Define the system instruction for the model
system_instruction = """You are a doctor. You must only reply to health-related questions.

You must solve queries, questions, and problems in an accurate and simple way.

You must not reply to any other topic or question.

If you are asked about anything else, just say 'I am a doctor, I can only answer health-related questions.'

Else if a user asks about health-related problems, you must reply in a very polite, simple, and easy-to-understand way."""

# Initialize the model with system instruction
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=system_instruction
)



@app.route('/ai')
def ai():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('ai.html')

@app.route('/logout')
def logout():
    session.clear()
    return render_template("index.html")


# API Routes for registration and login
@app.route('/api/register', methods=['POST'])
def api_register():
    """API endpoint for user registration"""
    try:
        # Log the incoming request
        print(f"Incoming registration request headers: {request.headers}")
        print(f"Incoming registration request data: {request.data}")
        
        if not request.is_json:
            print("Request is not JSON")
            return jsonify({"success": False, "message": "Request must be JSON"}), 400
            
        data = request.get_json()
        print(f"Parsed JSON data: {data}")
        
        if not data:
            print("No data in request")
            return jsonify({"success": False, "message": "No data provided"}), 400
            
        user_name = data.get('user_name', '').strip()
        contact_number = data.get('contact_number', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        confirm_password = data.get('confirm_password', '').strip()
        
        print(f"Extracted values - Name: {user_name}, Email: {email}, Contact: {contact_number}")
        
        # Validation
        validation_errors = []
        
        if not user_name:
            validation_errors.append("Username is required")
        if not contact_number:
            validation_errors.append("Contact number is required")
        if not email:
            validation_errors.append("Email is required")
        if not password:
            validation_errors.append("Password is required")
        if not confirm_password:
            validation_errors.append("Confirm password is required")
            
        if validation_errors:
            return jsonify({"success": False, "message": ", ".join(validation_errors)}), 400
        
        if password != confirm_password:
            return jsonify({"success": False, "message": "Passwords do not match"}), 400
        
        if len(password) < 6:
            return jsonify({"success": False, "message": "Password must be at least 6 characters"}), 400
        
        # Email validation
        if '@' not in email or '.' not in email:
            return jsonify({"success": False, "message": "Invalid email format"}), 400
        
        # Register user
        result = db.register_user(user_name, contact_number, email, password)
        print(f"Database registration result: {result}")
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        print(f"Registration error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"Registration failed: {str(e)}"}), 500
    
@app.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for user login"""
    print("\n=== LOGIN ATTEMPT ===")
    try:
        if not request.is_json:
            print("ERROR: Request is not JSON")
            return jsonify({"success": False, "message": "Request must be JSON"}), 400
            
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        
        print(f"Login attempt for email: {email}")
        
        if not email or not password:
            print("ERROR: Email or password missing")
            return jsonify({"success": False, "message": "Email and password are required"}), 400
        
        # Check credentials
        user = db.check_login(email, password)
        
        if user:
            print(f"SUCCESS: User found - ID: {user['id']}, Name: {user['user_name']}")
            
            # Set session
            session['user_id'] = user['id']
            session['user_name'] = user['user_name']
            session['email'] = user['email']
            
            print(f"Session set - User ID in session: {session.get('user_id')}")
            
            return jsonify({
                "success": True,
                "message": "Login successful",
                "user": {
                    "id": user['id'],
                    "name": user['user_name'],
                    "email": user['email']
                }
            }), 200
        else:
            print(f"FAILED: Invalid credentials for email: {email}")
            return jsonify({"success": False, "message": "Invalid email or password"}), 401
            
    except Exception as e:
        print(f"Login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": "Login failed"}), 500
    
@app.route('/api/logout', methods=['POST'])
def api_logout():
    """API endpoint for user logout"""
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully"}), 200

@app.route('/debug/session')
def debug_session():
    """Debug session information"""
    return jsonify({
        'session': dict(session),
        'logged_in': 'user_id' in session,
        'user_id': session.get('user_id'),
        'user_name': session.get('user_name')
    })

@app.route('/debug/database')
def debug_database():
    """Debug database users"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({
            'user_count': len(users),
            'users': users
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/check_session', methods=['GET'])
def check_session():
    """Check if user is logged in"""
    if 'user_id' in session:
        return jsonify({
            "logged_in": True,
            "user": {
                "id": session['user_id'],
                "name": session['user_name'],
                "email": session['email']
            }
        }), 200
    else:
        return jsonify({"logged_in": False}), 200
    

@app.route('/api/user/stats', methods=['GET'])
def get_user_stats():
    """Get user statistics for dashboard"""
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Please login first"}), 401
    
    user_id = session['user_id']
    stats = db.get_user_stats(user_id)
    
    return jsonify({
        "success": True,
        "stats": stats
    }), 200

@app.route('/api/symptoms/check', methods=['POST'])
def check_symptoms_api():
    """Check symptoms and save to history"""
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Please login first"}), 401
    
    try:
        data = request.get_json()
        symptoms = data.get('symptoms', '').strip()
        
        if not symptoms:
            return jsonify({"success": False, "message": "No symptoms provided"}), 400
        
        user_id = session['user_id']
        
        # Use Gemini AI to analyze symptoms
        prompt = f"""Analyze these symptoms: {symptoms}
        
        Provide the following information in JSON format:
        1. Possible conditions with probability
        2. Severity level (Low/Medium/High)
        3. Recommendations
        4. When to see a doctor
        5. Home remedies
        
        Format: {{"conditions": [], "severity": "", "recommendations": "", "see_doctor": "", "home_remedies": ""}}
        
        IMPORTANT: Do not include any markdown formatting, code blocks, or backticks in your response.
        Only return valid JSON format."""
        
        # Call Gemini AI
        response = model.generate_content(prompt)
        analysis_result = response.text
        
        # Clean the response
        clean_result = analysis_result.strip()
        
        # Remove any markdown code blocks
        if clean_result.startswith('```'):
            clean_result = clean_result.split('\n', 1)[1]  # Remove first line
        if clean_result.endswith('```'):
            clean_result = clean_result.rsplit('\n', 1)[0]  # Remove last line
        
        # Clean JSON string before parsing
        clean_result = clean_result.replace('\\n', ' ')  # Replace escaped newlines
        clean_result = ' '.join(clean_result.split())  # Remove extra whitespace
        
        # Try to parse as JSON
        try:
            result_data = json.loads(clean_result)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw response: {analysis_result}")
            print(f"Cleaned response: {clean_result}")
            # Fallback: Clean text without JSON structure
            result_data = {
                "analysis": analysis_result.replace('\n', '<br>').replace('\\n', '<br>'),
                "severity": "Unknown",
                "conditions": []
            }
        
        # Save cleaned result to database
        db.add_symptom_check(user_id, symptoms, json.dumps(result_data))
        
        return jsonify({
            "success": True,
            "symptoms": symptoms,
            "analysis": result_data
        }), 200
        
    except Exception as e:
        print(f"Symptoms check error: {str(e)}")
        traceback.print_exc()
        return jsonify({"success": False, "message": f"Error analyzing symptoms: {str(e)}"}), 500

@app.route('/api/chat', methods=['POST'])
def ai_chat():  # Changed function name
    try:
        data = request.get_json()
        question = data.get('question', '')
        if not question:
            return jsonify({"error": "No question provided"}), 400

        chat = model.start_chat(history=[])
        response = chat.send_message(question)

        return jsonify({"response": response.text})
    except Exception as e:
        print("=" * 50)
        print(f"ERROR TYPE: {type(e).__name__}")
        print(f"ERROR MESSAGE: {str(e)}")
        print("FULL TRACEBACK:")
        traceback.print_exc()
        print("=" * 50)
        
        return jsonify({"error": str(e)}), 500



@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        question = data.get('question', '')
        if not question:
            return jsonify({"error": "No question provided"}), 400

        chat = model.start_chat(history=[])
        response = chat.send_message(question)

        return jsonify({"response": response.text})
    except Exception as e:
        print("=" * 50)
        print(f"ERROR TYPE: {type(e).__name__}")
        print(f"ERROR MESSAGE: {str(e)}")
        print("FULL TRACEBACK:")
        traceback.print_exc()
        print("=" * 50)
        
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    # Initialize database tables
    print("Starting Health Advisor Application...")
    print("Initializing database...")
    db.create_tables()
    print("Database initialized")
    print(f"Secret key configured: {bool(app.secret_key)}")
    print(f"Database config: Host={db.host}, Database={db.database}")
    app.run(debug=True)
