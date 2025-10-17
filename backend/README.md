# Flask Backend Setup

## Installation

1. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Setup environment variables:
```bash
copy .env.example .env
```

4. Configure your `.env` file with:
- SUPABASE_URL: Your Supabase project URL
- SUPABASE_KEY: Your Supabase anon key
- JWT_SECRET: A secure random string

5. Run the database schema in Supabase SQL editor:
```sql
-- Copy and run the contents of database_schema.sql
```

6. Start the server:
```bash
python app.py
```

## API Endpoints

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/verify` - Verify JWT token