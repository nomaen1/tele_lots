import sqlite3

db_users = sqlite3.connect('lots.db')
cursor = db_users.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(255),
        name VARCHAR(255),
        lastname VARCHAR(255),
        round INTEGER DEFAULT 0,
        winner INTEGER DEFAULT 0,
        price INTEGER DEFAULT 0,
        agreement DATETIME
    ); 
""")
cursor.connection.commit()