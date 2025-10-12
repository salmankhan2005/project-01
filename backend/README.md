# MealPal Backend API

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure MongoDB Atlas:
   - Update `.env` file with your MongoDB Atlas connection string
   - Replace `<username>` and `<password>` with your credentials

3. Run the application:
```bash
python app.py
```

## API Endpoints

### Authentication

- **POST** `/api/auth/register` - Register new user
- **POST** `/api/auth/login` - Login user
- **GET** `/api/auth/verify` - Verify JWT token

### Request Examples

#### Register
```json
POST /api/auth/register
{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe"
}
```

#### Login
```json
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}
```

#### Verify Token
```
GET /api/auth/verify
Authorization: Bearer <jwt_token>
```