import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'feedback.db')


def _ensure_db():
    d = os.path.dirname(DB_PATH)
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            candidate TEXT,
            jd TEXT,
            rating INTEGER,
            comments TEXT
        )
    ''')
    conn.commit()
    conn.close()


def save_feedback(candidate, jd, rating, comments):
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('INSERT INTO feedback (timestamp, candidate, jd, rating, comments) VALUES (?, ?, ?, ?, ?)',
                (datetime.utcnow().isoformat(), candidate, jd, rating, comments))
    conn.commit()
    conn.close()


def list_feedback(limit=50):
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT timestamp, candidate, jd, rating, comments FROM feedback ORDER BY id DESC LIMIT ?', (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows
