-- Add status column to admin_recipes table
ALTER TABLE admin_recipes ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'published';