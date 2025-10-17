-- Create users table in Supabase
CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    phone VARCHAR(50),
    location VARCHAR(255),
    bio TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster email lookups
CREATE INDEX idx_users_email ON users(email);

-- Disable Row Level Security for custom authentication
ALTER TABLE users DISABLE ROW LEVEL SECURITY;

-- Alternative: If you want to keep RLS, use these policies instead:
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Allow insert for all" ON users FOR INSERT WITH CHECK (true);
-- CREATE POLICY "Allow select for all" ON users FOR SELECT USING (true);
-- CREATE POLICY "Allow update for all" ON users FOR UPDATE USING (true);