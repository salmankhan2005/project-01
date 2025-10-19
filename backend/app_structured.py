from flask import Flask, jsonify
from flask_cors import CORS
import logging
from config.settings import DEBUG_MODE, PORT, HOST
from routes.auth_routes import auth_bp

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Configure CORS
CORS(app, origins='*', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'], 
     allow_headers=['Content-Type', 'Authorization'])

# Register blueprints
app.register_blueprint(auth_bp)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Flask backend is running'}), 200

if __name__ == '__main__':
    print(f'Starting Flask server on http://{HOST}:{PORT}')
    print(f'Health check available at: http://{HOST}:{PORT}/api/health')
    app.run(debug=DEBUG_MODE, port=PORT, host=HOST)