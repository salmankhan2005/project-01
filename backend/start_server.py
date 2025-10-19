from app import app
import logging

# Set up logging to see errors
logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    print('Starting Flask server...')
    app.run(debug=True, port=5000, host='127.0.0.1')