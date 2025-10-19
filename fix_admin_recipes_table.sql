-- Drop and recreate admin_recipes table with all columns
DROP TABLE IF EXISTS admin_recipes CASCADE;

CREATE TABLE admin_recipes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    ingredients JSONB DEFAULT '[]',
    instructions JSONB DEFAULT '[]',
    cook_time INTEGER DEFAULT 30,
    servings INTEGER DEFAULT 1,
    difficulty VARCHAR(50) DEFAULT 'medium',
    category VARCHAR(100) DEFAULT 'Main',
    image VARCHAR(255) DEFAULT '🍽️',
    author VARCHAR(255) DEFAULT 'Admin',
    status VARCHAR(50) DEFAULT 'published',
    created_by INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_admin_recipe BOOLEAN DEFAULT TRUE
);