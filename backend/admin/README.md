# Admin Backend System

This is the admin backend system for the meal planning application with role-based access control.

## Admin Roles

### Super Admin
- Full system access
- Can manage all admin users
- Can access all features and settings
- Can create/delete other admins

### Sub Admin
- User management
- Recipe management
- Analytics viewing
- Content moderation

### Marketing Admin
- Marketing campaigns
- Analytics viewing
- Content moderation

## Setup

1. Copy `.env.example` to `.env` and configure your environment variables
2. Install dependencies: `pip install -r requirements.txt`
3. Run the database schema: Execute `schemas/admin_schema.sql` in your Supabase database
4. Start the server: `python admin_app.py` or run `run_admin.bat`

## API Endpoints

### Authentication
- `POST /api/admin/auth/login` - Admin login
- `GET /api/admin/auth/verify` - Verify admin token
- `POST /api/admin/auth/logout` - Admin logout

### Admin Management
- `GET /api/admin/users` - Get all admin users (requires admin_management permission)
- `POST /api/admin/users` - Create new admin user (requires admin_management permission)

## Default Permissions

### Super Admin
- user_management
- recipe_management
- analytics_view
- admin_management
- system_settings
- marketing_campaigns
- content_moderation

### Sub Admin
- user_management
- recipe_management
- analytics_view
- content_moderation

### Marketing Admin
- marketing_campaigns
- analytics_view
- content_moderation

## Security Features

- JWT token authentication
- Password hashing with Werkzeug
- Session management
- Role-based permissions
- IP address and user agent tracking
- Token expiration (8 hours)