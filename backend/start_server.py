import subprocess
import sys
import time
import requests

def check_server():
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        return response.status_code == 200
    except:
        return False

def start_server():
    print("Starting Flask backend server...")
    
    # Start the Flask app
    process = subprocess.Popen([sys.executable, 'app.py'])
    
    # Wait for server to start
    for i in range(10):
        time.sleep(1)
        if check_server():
            print("✅ Flask server is running on http://localhost:5000")
            print("✅ Health check: http://localhost:5000/api/health")
            break
        print(f"Waiting for server to start... ({i+1}/10)")
    else:
        print("❌ Server failed to start")
        process.terminate()
        return
    
    try:
        process.wait()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        process.terminate()

if __name__ == '__main__':
    start_server()