import requests
import json

# Test the minimal server
try:
    # Use the token from our previous test
    login_data = {'email': 'test@example.com', 'password': 'testpassword123'}
    login_response = requests.post('http://127.0.0.1:5000/api/auth/login', json=login_data)
    
    if login_response.status_code == 200:
        token = login_response.json()['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test the minimal server endpoint
        response = requests.get('http://127.0.0.1:5001/api/meal-plans/admin-templates', headers=headers)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print(f'Success! Found {len(data["templates"])} templates')
            for template in data['templates']:
                print(f'- {template["name"]}: {len(template["meals"])} days')
        else:
            print(f'Error: {response.text}')
    else:
        print(f'Login failed: {login_response.status_code}')
        
except Exception as e:
    print(f'Error: {e}')