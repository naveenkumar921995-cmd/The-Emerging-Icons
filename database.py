import sqlite3

def connect_db():
    conn = sqlite3.connect("data/stories.db")
    return conn

def create_table():
    conn = connect_db()
    cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    company TEXT,
    category TEXT,
    story TEXT,
    image TEXT,
    approved INTEGER DEFAULT 0
)
""")

    conn.commit()
    conn.close()
