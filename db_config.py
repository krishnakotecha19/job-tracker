from flask_mysqldb import MySQL

def init_db(app):
    app.config['MYSQL_HOST'] = 'switchback.proxy.rlwy.net'
    app.config['MYSQL_PORT'] = 23169
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'UGWIQalgOjSOaawYgFiUDuTIjYGUETmo'
    app.config['MYSQL_DB'] = 'railway'
    
    mysql = MySQL(app)
    return mysql
