# Recipe Synchronization System

This system enables the admin app to manage recipes that automatically sync to the meal plan app's discover page and recipe management.

## Architecture Overview

```
Admin App (Port 5001) ←→ Recipe Sync Service ←→ Meal Plan App (Port 5000)
                              ↓
                        Supabase Database
                    (admin_recipes, recipe_notifications)
```

## Features

### Admin App Features
- ✅ Create, edit, and delete recipes
- ✅ Recipe status management (draft/published)
- ✅ Automatic sync to meal plan apps
- ✅ Real-time notifications
- ✅ Recipe categorization and difficulty levels

### Meal Plan App Features
- ✅ Automatic discovery of admin recipes
- ✅ Admin recipes displayed with special styling
- ✅ Real-time polling for recipe updates
- ✅ Integration with existing recipe management
- ✅ Save admin recipes to personal collection

## Setup Instructions

### 1. Database Setup
```bash
# Run the setup script to create necessary tables
python setup_admin_recipes.py
```

### 2. Start Backend Services
```bash
# Terminal 1: Start main backend (Port 5000)
cd backend
python app.py

# Terminal 2: Start admin backend (Port 5001)
cd backend/admin
python admin_app.py
```

### 3. Start Frontend Applications
```bash
# Terminal 3: Start meal plan app
cd mealplan
npm run dev

# Terminal 4: Start admin app
cd admin
npm run dev
```

## How It Works

### Recipe Creation Flow
1. Admin creates/edits recipe in admin app
2. Recipe is saved to `admin_recipes` table
3. Sync service triggers:
   - Updates discover recipes
   - Creates notification in `recipe_notifications`
4. Meal plan app polls for updates every 60 seconds
5. New/updated recipes appear in discover page

### Recipe Deletion Flow
1. Admin deletes recipe in admin app
2. Recipe is removed from `admin_recipes` table
3. Sync service triggers:
   - Removes from discover recipes
   - Creates deletion notification
4. Meal plan app removes recipe from UI

## Database Tables

### admin_recipes
```sql
- id (Primary Key)
- title (Recipe name)
- description
- ingredients (JSON array)
- instructions (JSON array)
- cook_time (minutes)
- servings
- difficulty (easy/medium/hard)
- category
- image (emoji or URL)
- author
- status (draft/published)
- created_by (admin user ID)
- created_at, updated_at
- is_admin_recipe (boolean flag)
```

### recipe_notifications
```sql
- id (Primary Key)
- type (recipe_change)
- action (create/update/delete)
- recipe_id
- recipe_title
- timestamp
- data (JSON with recipe details)
- processed (boolean)
```

## API Endpoints

### Admin Backend (Port 5001)
- `GET /api/admin/recipes` - Get all admin recipes
- `POST /api/admin/recipes` - Create new recipe
- `PUT /api/admin/recipes/:id` - Update recipe
- `DELETE /api/admin/recipes/:id` - Delete recipe
- `GET /api/admin/recipes/discover` - Get published recipes for discover
- `GET /api/admin/recipes/sync` - Get recipe notifications

### Main Backend (Port 5000)
- `GET /api/discover/recipes` - Get all recipes (includes admin recipes)
- `GET /api/recipes/:id/details` - Get recipe details

## Real-time Synchronization

The system uses polling-based synchronization:

1. **Admin App**: Immediately updates local state after CRUD operations
2. **Sync Service**: Creates notifications for each recipe change
3. **Meal Plan App**: Polls every 60 seconds for new notifications
4. **Fallback**: If admin backend is unavailable, meal plan app continues with existing recipes

## Configuration

### Environment Variables
```env
# Admin backend runs on different port
ADMIN_PORT=5001
PORT=5000

# Same Supabase credentials for both apps
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
ADMIN_JWT_SECRET=your_admin_jwt_secret
```

### Frontend Configuration
```typescript
// Admin API URL
VITE_ADMIN_API_URL=http://127.0.0.1:5001/api/admin

// Main API URL  
VITE_API_URL=http://127.0.0.1:5000/api
```

## Testing the Integration

1. **Create Recipe in Admin**:
   - Open admin app
   - Go to Recipes section
   - Create a new recipe
   - Set status to "Published"

2. **Verify in Meal Plan App**:
   - Open meal plan app
   - Go to Discover page
   - Admin recipe should appear with green "Admin Recipe" badge
   - Recipe should also appear in Recipes page under "Admin Recipes" section

3. **Test Updates**:
   - Edit recipe in admin app
   - Changes should reflect in meal plan app within 60 seconds

4. **Test Deletion**:
   - Delete recipe in admin app
   - Recipe should disappear from meal plan app

## Troubleshooting

### Common Issues

1. **Recipes not syncing**:
   - Check if admin backend is running on port 5001
   - Verify database connection
   - Check browser console for API errors

2. **Database errors**:
   - Run `python setup_admin_recipes.py` again
   - Check Supabase credentials
   - Verify table permissions

3. **Port conflicts**:
   - Admin backend uses port 5001
   - Main backend uses port 5000
   - Ensure both ports are available

### Debug Mode
Enable debug logging in both backends:
```bash
export FLASK_DEBUG=true
```

## Future Enhancements

- [ ] WebSocket-based real-time sync
- [ ] Recipe image upload functionality
- [ ] Recipe approval workflow
- [ ] Bulk recipe import/export
- [ ] Recipe analytics and usage tracking
- [ ] Recipe versioning system

## Security Considerations

- Admin recipes require admin authentication
- Recipe notifications are public (for meal plan apps)
- Input validation on all recipe fields
- SQL injection protection via parameterized queries
- CORS properly configured for cross-origin requests