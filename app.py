from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mysqldb import MySQL
import os

app = Flask(__name__)
CORS(app, supports_credentials=True, origins="*")  # Adjusted origin

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


# --- Jobs Routes ---

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
        cursor.execute(
            "INSERT INTO jobs (company, role, date, status, notes) VALUES (%s, %s, %s, %s, %s)",
            (company, role, date, status, notes)
        )
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
        cursor.execute("SELECT id, company, role, date, status, notes FROM jobs ORDER BY date DESC")
        rows = cursor.fetchall()
        cursor.close()

        jobs = []
        for row in rows:
            if 'date' in row and row['date']:
                row['date'] = row['date'].strftime("%Y-%m-%d")
            jobs.append(row)
        return jsonify(jobs), 200
    except Exception as e:
        print(f"Error fetching jobs: {str(e)}")
        return jsonify({"message": f"Error fetching jobs: {str(e)}"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()

@app.route('/job/<int:id>', methods=['DELETE'])
def delete_job(id):
    cursor = mysql.connection.cursor()
    try:
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
    app.run(debug=True,port=5000 )