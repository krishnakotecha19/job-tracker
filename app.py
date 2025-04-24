from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
from flask_session import Session

app = Flask(__name__)
CORS(app)


app.config['SECRET_KEY'] = 'a3b1c8d4e9f2071a8b5c6d3e2f019476' 
app.config['SESSION_TYPE'] = 'filesystem' 
Session(app)


app.config['MYSQL_HOST'] = 'shuttle.proxy.rlwy.net'
app.config['MYSQL_PORT'] = 12271
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'PkvrsVLVfKUEqmQUwlkLtzVZGMHMFXwt'
app.config['MYSQL_DB'] = 'railway'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

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
        # IMPORTANT CHANGE HERE: Do not include 'id' in the INSERT statement
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        mysql.connection.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"message": f"Registration failed: {str(e)}"}), 500
    finally:
        cursor.close()

# --- User Login Route ---
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
            session['user_id'] = user['id']  # Store user ID in session
            return jsonify({"message": "Login successful"}), 200
        else:
            return jsonify({"message": "Invalid username or password"}), 401
    except Exception as e:
        return jsonify({"message": f"Login failed: {str(e)}"}), 500
    finally:
        cursor.close()


@app.route('/job', methods=['POST'])
def add_job():
    data = request.get_json()
    company = data['company']
    role = data['role']
    date = data['date']
    status = data['status']
    notes = data.get('notes', '')

    cursor = mysql.connection.cursor()
    try:
        cursor.execute("INSERT INTO jobs (company, role, date, status, notes) VALUES (%s, %s, %s, %s, %s)",
                       (company, role, date, status, notes))
        mysql.connection.commit()
        return jsonify({"message": "Job added successfully"}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"message": f"Error adding job: {str(e)}"}), 500
    finally:
        cursor.close()

@app.route('/job', methods=['GET'])
def get_all_jobs():
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT * FROM jobs")
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
def delete_job(id):
    cursor = mysql.connection.cursor()
    try:
        # Check if job exists
        cursor.execute("SELECT * FROM jobs WHERE id = %s", (id,))
        job = cursor.fetchone()

        if job:
            cursor.execute("DELETE FROM jobs WHERE id = %s", (id,))
            mysql.connection.commit()
            return jsonify({"message": "Job deleted successfully"}), 200
        else:
            return jsonify({"message": "Job not found"}), 404
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"message": f"Error deleting job: {str(e)}"}), 500
    finally:
        cursor.close()

if __name__ == '__main__':
    app.run(debug=True)