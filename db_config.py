from flask_mysqldb import MySQL

def init_db(app):
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'  # or your username
    app.config['MYSQL_PASSWORD'] = 'root'  # update this
    app.config['MYSQL_DB'] = 'job_tracker'
    
    mysql = MySQL(app)
    return mysql
