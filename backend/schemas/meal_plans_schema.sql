-- Create meal_plans table
CREATE TABLE IF NOT EXISTS meal_plans (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    week_name VARCHAR(255) NOT NULL,
    meal_type VARCHAR(50) NOT NULL,
    recipe_id VARCHAR(255),
    recipe_name VARCHAR(255),
    recipe_data JSONB,
    planned_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_meal_plans_user_id ON meal_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_meal_plans_week ON meal_plans(week_name);
CREATE INDEX IF NOT EXISTS idx_meal_plans_date ON meal_plans(planned_date);

-- Disable Row Level Security
ALTER TABLE meal_plans DISABLE ROW LEVEL SECURITY;