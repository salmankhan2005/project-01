-- Create admin_users table
CREATE TABLE IF NOT EXISTS admin_users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('super_admin', 'sub_admin', 'marketing_admin')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    created_by UUID REFERENCES admin_users(id)
);

-- Create admin_sessions table for session management
CREATE TABLE IF NOT EXISTS admin_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    admin_id UUID REFERENCES admin_users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT
);

-- Create admin_permissions table
CREATE TABLE IF NOT EXISTS admin_permissions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create admin_role_permissions table
CREATE TABLE IF NOT EXISTS admin_role_permissions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    role VARCHAR(50) NOT NULL,
    permission_id UUID REFERENCES admin_permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(role, permission_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_admin_users_email ON admin_users(email);
CREATE INDEX IF NOT EXISTS idx_admin_users_role ON admin_users(role);
CREATE INDEX IF NOT EXISTS idx_admin_sessions_admin_id ON admin_sessions(admin_id);
CREATE INDEX IF NOT EXISTS idx_admin_sessions_expires ON admin_sessions(expires_at);

-- Insert default permissions
INSERT INTO admin_permissions (name, description) VALUES
('user_management', 'Manage regular users'),
('recipe_management', 'Manage recipes and content'),
('analytics_view', 'View analytics and reports'),
('admin_management', 'Manage admin users'),
('system_settings', 'Manage system settings'),
('marketing_campaigns', 'Manage marketing campaigns'),
('content_moderation', 'Moderate user content')
ON CONFLICT (name) DO NOTHING;

-- Insert default role permissions
INSERT INTO admin_role_permissions (role, permission_id) 
SELECT 'super_admin', id FROM admin_permissions
ON CONFLICT (role, permission_id) DO NOTHING;

INSERT INTO admin_role_permissions (role, permission_id) 
SELECT 'sub_admin', id FROM admin_permissions WHERE name IN ('user_management', 'recipe_management', 'analytics_view', 'content_moderation')
ON CONFLICT (role, permission_id) DO NOTHING;

INSERT INTO admin_role_permissions (role, permission_id) 
SELECT 'marketing_admin', id FROM admin_permissions WHERE name IN ('marketing_campaigns', 'analytics_view', 'content_moderation')
ON CONFLICT (role, permission_id) DO NOTHING;

-- Disable Row Level Security for custom authentication
ALTER TABLE admin_users DISABLE ROW LEVEL SECURITY;
ALTER TABLE admin_sessions DISABLE ROW LEVEL SECURITY;
ALTER TABLE admin_permissions DISABLE ROW LEVEL SECURITY;
ALTER TABLE admin_role_permissions DISABLE ROW LEVEL SECURITY;