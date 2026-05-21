import sqlite3
import json
from config import DATABASE

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS pending_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, username TEXT, content_type TEXT, content TEXT,
            footer TEXT, timestamp INTEGER)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS bot_settings (
            key TEXT PRIMARY KEY, value TEXT)''')
        conn.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('post_footer', '')")

def add_post(user_id, username, content_type, content, footer=""):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("INSERT INTO pending_posts (user_id, username, content_type, content, footer, timestamp) VALUES (?,?,?,?,?,?)",
                              (user_id, username, content_type, content, footer, int(time.time())))
        return cursor.lastrowid

def get_pending_posts():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("SELECT id, user_id, username, content_type, content, footer FROM pending_posts ORDER BY timestamp")
        return cursor.fetchall()

def get_post_by_id(post_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("SELECT id, user_id, username, content_type, content, footer FROM pending_posts WHERE id=?", (post_id,))
        return cursor.fetchone()

def delete_post(post_id):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("DELETE FROM pending_posts WHERE id=?", (post_id,))

def get_setting(key, default=""):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("SELECT value FROM bot_settings WHERE key=?", (key,))
        row = cursor.fetchone()
        return row[0] if row else default

def set_setting(key, value):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("REPLACE INTO bot_settings (key, value) VALUES (?,?)", (key, value))