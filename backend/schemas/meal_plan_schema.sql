-- Create meal_plans table
CREATE TABLE IF NOT EXISTS meal_plans (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    recipe_id VARCHAR(255) NOT NULL,
    recipe_name VARCHAR(255) NOT NULL,
    day VARCHAR(20) NOT NULL,
    meal_time VARCHAR(20) NOT NULL,
    servings INTEGER DEFAULT 1,
    image VARCHAR(255) DEFAULT '🍽️',
    time VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster meal plan lookups
CREATE INDEX IF NOT EXISTS idx_meal_plans_user_id ON meal_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_meal_plans_day ON meal_plans(day);
CREATE INDEX IF NOT EXISTS idx_meal_plans_user_day ON meal_plans(user_id, day);

-- Disable Row Level Security for custom authentication
ALTER TABLE meal_plans DISABLE ROW LEVEL SECURITY;