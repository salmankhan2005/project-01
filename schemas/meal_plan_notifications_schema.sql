-- Meal Plan Notifications Table
-- Handles synchronization between admin and user apps

CREATE TABLE IF NOT EXISTS meal_plan_notifications (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL DEFAULT 'meal_plan_update',
    action VARCHAR(20) NOT NULL, -- 'create', 'update', 'delete'
    meal_plan_id INTEGER,
    meal_plan_data JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processed'
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_meal_plan_notifications_timestamp ON meal_plan_notifications(timestamp);
CREATE INDEX IF NOT EXISTS idx_meal_plan_notifications_status ON meal_plan_notifications(status);
CREATE INDEX IF NOT EXISTS idx_meal_plan_notifications_type ON meal_plan_notifications(type);

-- Add columns to existing meal_plans table for admin sync
ALTER TABLE meal_plans ADD COLUMN IF NOT EXISTS is_admin_generated BOOLEAN DEFAULT FALSE;
ALTER TABLE meal_plans ADD COLUMN IF NOT EXISTS admin_meal_plan_id INTEGER;
ALTER TABLE meal_plans ADD COLUMN IF NOT EXISTS template_applied_at TIMESTAMP WITH TIME ZONE;

-- Create indexes for new columns
CREATE INDEX IF NOT EXISTS idx_meal_plans_admin_generated ON meal_plans(is_admin_generated);
CREATE INDEX IF NOT EXISTS idx_meal_plans_admin_id ON meal_plans(admin_meal_plan_id);

-- Update admin_meal_plans table structure if needed
ALTER TABLE admin_meal_plans ADD COLUMN IF NOT EXISTS sync_enabled BOOLEAN DEFAULT TRUE;
ALTER TABLE admin_meal_plans ADD COLUMN IF NOT EXISTS last_synced_at TIMESTAMP WITH TIME ZONE;

-- Create a view for active admin meal plans
CREATE OR REPLACE VIEW active_admin_meal_plans AS
SELECT 
    id,
    name,
    description,
    week_start,
    meals,
    created_by,
    status,
    created_at,
    updated_at,
    sync_enabled,
    last_synced_at
FROM admin_meal_plans 
WHERE status = 'active' AND sync_enabled = TRUE;

-- Function to automatically create notifications when admin meal plans change
CREATE OR REPLACE FUNCTION notify_meal_plan_change()
RETURNS TRIGGER AS $$
BEGIN
    -- Only create notifications for active plans with sync enabled
    IF (TG_OP = 'DELETE') THEN
        IF OLD.status = 'active' AND OLD.sync_enabled = TRUE THEN
            INSERT INTO meal_plan_notifications (
                action, 
                meal_plan_id, 
                meal_plan_data,
                timestamp
            ) VALUES (
                'delete',
                OLD.id,
                row_to_json(OLD),
                NOW()
            );
        END IF;
        RETURN OLD;
    ELSIF (TG_OP = 'UPDATE') THEN
        IF NEW.status = 'active' AND NEW.sync_enabled = TRUE THEN
            INSERT INTO meal_plan_notifications (
                action, 
                meal_plan_id, 
                meal_plan_data,
                timestamp
            ) VALUES (
                'update',
                NEW.id,
                row_to_json(NEW),
                NOW()
            );
        END IF;
        RETURN NEW;
    ELSIF (TG_OP = 'INSERT') THEN
        IF NEW.status = 'active' AND NEW.sync_enabled = TRUE THEN
            INSERT INTO meal_plan_notifications (
                action, 
                meal_plan_id, 
                meal_plan_data,
                timestamp
            ) VALUES (
                'create',
                NEW.id,
                row_to_json(NEW),
                NOW()
            );
        END IF;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic notifications
DROP TRIGGER IF EXISTS meal_plan_change_trigger ON admin_meal_plans;
CREATE TRIGGER meal_plan_change_trigger
    AFTER INSERT OR UPDATE OR DELETE ON admin_meal_plans
    FOR EACH ROW EXECUTE FUNCTION notify_meal_plan_change();

-- Clean up old notifications (keep last 1000 records)
CREATE OR REPLACE FUNCTION cleanup_old_notifications()
RETURNS void AS $$
BEGIN
    DELETE FROM meal_plan_notifications 
    WHERE id NOT IN (
        SELECT id FROM meal_plan_notifications 
        ORDER BY timestamp DESC 
        LIMIT 1000
    );
END;
$$ LANGUAGE plpgsql;

-- Create a scheduled job to clean up old notifications (if using pg_cron extension)
-- SELECT cron.schedule('cleanup-meal-plan-notifications', '0 2 * * *', 'SELECT cleanup_old_notifications();');

COMMENT ON TABLE meal_plan_notifications IS 'Stores notifications for meal plan changes to sync between admin and user apps';
COMMENT ON COLUMN meal_plan_notifications.type IS 'Type of notification (meal_plan_update, etc.)';
COMMENT ON COLUMN meal_plan_notifications.action IS 'Action performed (create, update, delete)';
COMMENT ON COLUMN meal_plan_notifications.meal_plan_data IS 'Complete meal plan data as JSON';
COMMENT ON COLUMN meal_plan_notifications.status IS 'Processing status (pending, processed)';