from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
from flask_session import Session
from functools import wraps
import os

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://127.0.0.1:5500"])

# Secret Key and Session Configuration
app.config['SECRET_KEY'] = 'a3b1c8d4e9f2071a8b5c6d3e2f019476'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['SESSION_FILE_DIR'] = os.path.join(app.root_path, 'flask_sessions')
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'job_tracker_session_'
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_DOMAIN'] = '.localhost'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax' # Or 'None' for testing
app.config['SESSION_COOKIE_SECURE'] = False # Set to True in production with HTTPS




os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
Session(app)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'shuttle.proxy.rlwy.net'
app.config['MYSQL_PORT'] = 12271
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'PkvrsVLVfKUEqmQUwlkLtzVZGMHMFXwt'
app.config['MYSQL_DB'] = 'railway'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# --- Routes ---

@app.route('/')
def home():
    return "Welcome to Job Tracker API!"

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            return jsonify({"message": "Username already exists"}), 409

        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        mysql.connection.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"message": f"Registration failed: {str(e)}"}), 500
    finally:
        cursor.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session.permanent = True  # Ensure the session is permanent
            #  Set the domain for the session cookie
           
            print(f"Session set for user: {user['id']}")
            return jsonify({"message": "Login successful"}), 200
        else:
            return jsonify({"message": "Invalid username or password"}), 401
    except Exception as e:
        return jsonify({"message": f"Login failed: {str(e)}"}), 500
    finally:
        cursor.close()



# --- Authentication Decorator ---
def login_required(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"message": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_view

# --- Jobs Routes ---

@app.route('/job', methods=['POST'])
@login_required
def add_job():
    data = request.get_json()
    company = data['company']
    role = data['role']
    date = data['date']
    status = data['status']
    notes = data.get('notes', '')
    user_id = session['user_id']

    cursor = mysql.connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO jobs (company, role, date, status, notes, user_id) VALUES (%s, %s, %s, %s, %s, %s)",
            (company, role, date, status, notes, user_id)
        )
        mysql.connection.commit()
        return jsonify({"message": "Job added successfully"}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"message": f"Error adding job: {str(e)}"}), 500
    finally:
        cursor.close()

@app.route('/job', methods=['GET'])
@login_required
def get_all_jobs():
    user_id = session['user_id']
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT * FROM jobs WHERE user_id = %s ORDER BY date DESC", (user_id,))
        rows = cursor.fetchall()
        jobs = []
        for row in rows:
            jobs.append({
                "id": row['id'],
                "company": row['company'],
                "role": row['role'],
                "date": row['date'].strftime("%Y-%m-%d"),
                "status": row['status'],
                "notes": row['notes']
            })
        return jsonify(jobs), 200
    except Exception as e:
        return jsonify({"message": f"Error fetching jobs: {str(e)}"}), 500
    finally:
        cursor.close()

@app.route('/job/<int:id>', methods=['DELETE'])
@login_required
def delete_job(id):
    user_id = session['user_id']
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT * FROM jobs WHERE id = %s AND user_id = %s", (id, user_id))
        job = cursor.fetchone()

        if job:
            cursor.execute("DELETE FROM jobs WHERE id = %s AND user_id = %s", (id, user_id))
            mysql.connection.commit()
            return jsonify({"message": "Job deleted successfully"}), 200
        else:
            return jsonify({"message": "Job not found or does not belong to you"}), 404
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"message": f"Error deleting job: {str(e)}"}), 500
    finally:
        cursor.close()
        
@app.route('/auth-status')
def auth_status():
    print(f"Session data: {session}")
    if 'user_id' in session:
        return jsonify({"logged_in": True}), 200
    else:
        return jsonify({"logged_in": False}), 401

if __name__ == '__main__':
    app.run(debug=True,port=5000)
