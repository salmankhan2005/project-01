-- Create recipes table (for original recipes created by users)
CREATE TABLE IF NOT EXISTS recipes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    ingredients JSONB DEFAULT '[]'::jsonb,
    instructions JSONB DEFAULT '[]'::jsonb,
    prep_time INTEGER,
    cook_time INTEGER,
    servings INTEGER DEFAULT 1,
    difficulty VARCHAR(50) DEFAULT 'medium',
    tags JSONB DEFAULT '[]'::jsonb,
    image VARCHAR(255) DEFAULT '🍽️',
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add image column if it doesn't exist (for existing tables)
ALTER TABLE recipes ADD COLUMN IF NOT EXISTS image VARCHAR(255) DEFAULT '🍽️';

-- Create index for faster user recipe lookups
CREATE INDEX IF NOT EXISTS idx_recipes_user_id ON recipes(user_id);

-- Disable Row Level Security for custom authentication
ALTER TABLE recipes DISABLE ROW LEVEL SECURITY;