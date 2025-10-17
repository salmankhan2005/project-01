from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/auth/login', methods=['POST'])
def login():
    return jsonify({'message': 'Login successful', 'token': 'test-token', 'user': {'id': '1', 'email': 'test@test.com'}})

@app.route('/api/auth/register', methods=['POST'])
def register():
    return jsonify({'message': 'User created', 'token': 'test-token', 'user': {'id': '1', 'email': 'test@test.com'}})

if __name__ == '__main__':
    print('Simple Flask server starting on http://localhost:5000')
    app.run(debug=True, port=5000, host='127.0.0.1')