#!/usr/bin/env python3

print("Run this SQL in your Supabase SQL Editor to create analytics table:")
print("=" * 60)

sql = """
-- Create user_analytics table
CREATE TABLE IF NOT EXISTS user_analytics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for analytics queries
CREATE INDEX IF NOT EXISTS idx_analytics_user_id ON user_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_event_type ON user_analytics(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_created_at ON user_analytics(created_at);
CREATE INDEX IF NOT EXISTS idx_analytics_user_event ON user_analytics(user_id, event_type);

-- Disable Row Level Security
ALTER TABLE user_analytics DISABLE ROW LEVEL SECURITY;
"""

print(sql)
print("=" * 60)