# FreshPlate - Smart Meal Planner

A full-stack meal planning application with React frontend and Flask backend using Supabase database.

## Features

- User authentication (register/login)
- Profile management
- Meal planning and recipe management
- Real-time data synchronization
- Responsive design

## Tech Stack

### Frontend
- React + TypeScript
- Vite
- Tailwind CSS
- shadcn/ui components
- React Router

### Backend
- Python Flask
- Supabase (PostgreSQL)
- JWT authentication
- CORS enabled

## Setup Instructions

### Frontend Setup
```bash
cd mealplan
npm install
npm run dev
```

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Configure your .env file with Supabase credentials
python app.py
```

### Database Setup
1. Create a Supabase project
2. Run the SQL commands from `backend/database_schema.sql`
3. Update `.env` with your Supabase credentials

## Environment Variables

Create `backend/.env` file:
```
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-anon-key
JWT_SECRET=your-jwt-secret
```

## API Endpoints

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/verify` - Token verification
- `PUT /api/profile/update` - Update user profile

## Development

- Frontend runs on `http://localhost:8080`
- Backend runs on `http://localhost:5000`

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request