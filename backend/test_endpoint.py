import requests
import json

# Test the admin templates endpoint
try:
    # First get a token by registering/logging in
    login_data = {'email': 'test@example.com', 'password': 'testpassword123'}
    
    # Try to register first
    register_response = requests.post('http://127.0.0.1:5000/api/auth/register', json=login_data)
    if register_response.status_code == 201:
        token = register_response.json()['token']
        print('Registered new user')
    else:
        # Try to login
        login_response = requests.post('http://127.0.0.1:5000/api/auth/login', json=login_data)
        if login_response.status_code == 200:
            token = login_response.json()['token']
            print('Logged in existing user')
        else:
            print(f'Login failed: {login_response.status_code} - {login_response.text}')
            exit(1)
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test the admin templates endpoint
    response = requests.get('http://127.0.0.1:5000/api/meal-plans/admin-templates', headers=headers)
    print(f'Status: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'Found {len(data["templates"])} templates')
        for template in data['templates']:
            print(f'- {template["name"]}: {len(template["meals"])} days, {sum(len(day_meals) for day_meals in template["meals"].values())} meals')
    else:
        print(f'Error response: {response.text}')
        
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()