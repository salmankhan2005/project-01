from app import app
import os

if __name__ == '__main__':
    # Production settings
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    host = '127.0.0.1' if debug_mode else '0.0.0.0'
    app.run(debug=debug_mode, host=host, port=5000)