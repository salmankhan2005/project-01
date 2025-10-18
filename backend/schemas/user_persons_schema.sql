-- Create user_persons table for managing people in meal planning
CREATE TABLE IF NOT EXISTS user_persons (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    preferences TEXT,
    allergies TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_user_persons_user_id ON user_persons(user_id);

-- Disable Row Level Security
ALTER TABLE user_persons DISABLE ROW LEVEL SECURITY;