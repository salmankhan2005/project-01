"""
Simple health check endpoint for the backend API
"""
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Backend server is running',
        'timestamp': '2024-01-01T00:00:00Z'
    }), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)