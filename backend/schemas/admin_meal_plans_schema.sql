-- Admin Meal Plans Table
CREATE TABLE IF NOT EXISTS admin_meal_plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    week_start DATE,
    meals JSONB DEFAULT '{}',
    created_by VARCHAR(100) DEFAULT 'admin',
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_admin_meal_plans_status ON admin_meal_plans(status);
CREATE INDEX IF NOT EXISTS idx_admin_meal_plans_created_at ON admin_meal_plans(created_at);
CREATE INDEX IF NOT EXISTS idx_admin_meal_plans_week_start ON admin_meal_plans(week_start);