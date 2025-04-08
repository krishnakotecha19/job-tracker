from flask_mysqldb import MySQL

def init_db(app):
    app.config['MYSQL_HOST'] = 'shuttle.proxy.rlwy.net'
    app.config['MYSQL_PORT'] = 12271
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'PkvrsVLVfKUEqmQUwlkLtzVZGMHMFXwt'
    app.config['MYSQL_DB'] = 'railway'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    return MySQL(app)
