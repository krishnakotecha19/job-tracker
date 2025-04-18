from flask import Flask, request, jsonify
from flask_cors import CORS

from db_config import init_db

app = Flask(__name__)
CORS(app)
mysql = init_db(app)

@app.route('/')
def home():
    return "Welcome to Job Tracker API!"

@app.route('/job', methods=['POST'])
def add_job():
    data = request.get_json()
    company = data['company']
    role = data['role']
    date = data['date']
    status = data['status']
    notes = data.get('notes', '')

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO jobs (company, role, date, status, notes) VALUES (%s, %s, %s, %s, %s)",
                   (company, role, date, status, notes))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "Job added successfully"}), 201

@app.route('/job', methods=['GET'])
def get_all_jobs():
    cursor = mysql.connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM jobs")
    rows = cursor.fetchall()
    cursor.close()

    jobs = []
    for row in rows:
        jobs.append({
            "id": row["id"],
            "company": row["company"],
            "role": row["role"],
            "date": row["date"].strftime("%Y-%m-%d"),
            "status": row["status"],
            "notes": row["notes"]
        })

    return jsonify(jobs), 200

@app.route('/job/<status>', methods=['GET'])
def get_jobs_by_status(status):
    cursor = mysql.connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM jobs WHERE status = %s", (status,))
    rows = cursor.fetchall()
    cursor.close()

    jobs = []
    for row in rows:
        jobs.append({
            "id": row["id"],
            "company": row["company"],
            "role": row["role"],
            "date": row["date"].strftime("%Y-%m-%d"),
            "status": row["status"],
            "notes": row["notes"]
        })

    return jsonify(jobs), 200

@app.route('/job/<int:id>', methods=['DELETE'])
def delete_job(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM jobs WHERE id = %s", (id,))
    job = cursor.fetchone()

    if job:
        cursor.execute("DELETE FROM jobs WHERE id = %s", (id,))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"message": "Job deleted successfully"}), 200
    else:
        cursor.close()
        return jsonify({"message": "Job not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
