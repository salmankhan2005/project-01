-- Notifications table for Supabase
CREATE TABLE IF NOT EXISTS notifications (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    target_audience TEXT DEFAULT 'All Users',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

-- User notification read status
CREATE TABLE IF NOT EXISTS user_notification_status (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT,
    notification_id BIGINT REFERENCES notifications(id),
    is_read BOOLEAN DEFAULT false,
    read_at TIMESTAMPTZ,
    is_deleted BOOLEAN DEFAULT false,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, notification_id)
);

