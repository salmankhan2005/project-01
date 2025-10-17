from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/auth/login', methods=['POST'])
def login():
    # This is a test endpoint - implement proper authentication
    return jsonify({'message': 'Test endpoint - implement proper auth'}), 501

@app.route('/api/auth/register', methods=['POST'])
def register():
    # This is a test endpoint - implement proper authentication
    return jsonify({'message': 'Test endpoint - implement proper auth'}), 501

if __name__ == '__main__':
    import os
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    print('Simple Flask server starting on http://localhost:5000')
    app.run(debug=debug_mode, port=5000, host='127.0.0.1')