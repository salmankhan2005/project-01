from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = sqlite3.connect('notifications.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            target_audience TEXT DEFAULT 'All Users',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/api/notifications', methods=['POST'])
def create_notification():
    data = request.json
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO notifications (title, message, target_audience) VALUES (?, ?, ?)',
        (data['title'], data['message'], data.get('target_audience', 'All Users'))
    )
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Notification created'})

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    conn = get_db_connection()
    notifications = conn.execute(
        'SELECT * FROM notifications WHERE is_active = 1 ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    
    return jsonify([{
        'id': row['id'],
        'title': row['title'],
        'message': row['message'],
        'target_audience': row['target_audience'],
        'created_at': row['created_at']
    } for row in notifications])

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)