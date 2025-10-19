# Meal Plan Synchronization System

This document describes the meal plan synchronization feature that allows admin-created meal plans to be synced to user apps.

## Overview

The meal plan sync system enables:
- **Admin App**: Create, edit, and manage meal plan templates
- **User App**: Browse and apply admin-created meal plan templates
- **Real-time Sync**: Automatic synchronization between admin and user apps
- **Template System**: Users can apply pre-made meal plans to their weekly schedules

## Architecture

### Backend Components

1. **Main Backend** (`backend/app.py`)
   - Handles user meal plan operations
   - Provides template browsing and application endpoints
   - Manages meal plan sync notifications

2. **Admin Backend** (`backend/admin/admin_app.py`)
   - Handles admin meal plan creation and management
   - Triggers sync notifications when meal plans change
   - Provides admin-specific meal plan endpoints

3. **Sync Service** (`backend/meal_plan_sync.py`)
   - Manages synchronization between admin and user apps
   - Creates notifications for meal plan changes
   - Formats meal plans for user consumption

### Database Schema

1. **admin_meal_plans** - Stores admin-created meal plan templates
2. **meal_plan_notifications** - Tracks sync notifications
3. **meal_plans** - User meal plans (enhanced with admin sync fields)

### Frontend Components

1. **Admin App**
   - `EnhancedMealPlans.tsx` - Advanced meal plan creation with detailed scheduling
   - `MealPlans.tsx` - Basic meal plan management

2. **User App**
   - `MealPlanTemplates.tsx` - Browse and apply admin templates
   - `Home.tsx` - Enhanced with template browsing button
   - `mealPlanSync.ts` - Sync service for template operations

## Features

### Admin Features

- **Create Detailed Meal Plans**: Schedule meals for each day and meal time
- **Meal Plan Management**: Edit, delete, and manage meal plan status
- **Automatic Sync**: Changes automatically sync to user apps
- **Template Preview**: See how meal plans will appear to users

### User Features

- **Browse Templates**: View all available admin-created meal plans
- **Template Preview**: See meal counts, days covered, and sample meals
- **Apply Templates**: Apply templates to specific weeks
- **Sync Notifications**: Get notified of new or updated templates

## API Endpoints

### Admin Endpoints

```
GET    /api/admin/meal-plans           - Get all admin meal plans
POST   /api/admin/meal-plans           - Create new meal plan
PUT    /api/admin/meal-plans/:id       - Update meal plan
DELETE /api/admin/meal-plans/:id       - Delete meal plan
```

### User Endpoints

```
GET    /api/meal-plans/admin-templates - Get available templates
POST   /api/meal-plans/apply-template  - Apply template to user plan
GET    /api/meal-plans/sync            - Get sync notifications
```

## Setup Instructions

### 1. Database Setup

Run the meal plan sync setup script:

```bash
cd backend
python setup_meal_plan_sync.py
```

This will:
- Create necessary database tables
- Set up sync triggers
- Create sample meal plan templates

### 2. Backend Setup

Start both backend services:

```bash
# Main backend (port 5000)
cd backend
python app.py

# Admin backend (port 5001)
cd backend/admin
python admin_app.py
```

### 3. Frontend Setup

Start both frontend applications:

```bash
# User app (port 5173)
cd mealplan
npm run dev

# Admin app (port 5174)
cd admin
npm run dev
```

## Usage Workflow

### Admin Workflow

1. **Login to Admin App** (`http://localhost:5174`)
2. **Navigate to Enhanced Meal Plans**
3. **Create New Meal Plan**:
   - Enter plan name and description
   - Set week start date
   - Add meals for each day/time combination
   - Set status to "active"
4. **Save Plan** - Automatically syncs to user apps

### User Workflow

1. **Login to User App** (`http://localhost:5173`)
2. **Navigate to Home Page**
3. **Click "Browse Templates"**
4. **Select Template**:
   - View template details
   - Choose target week
   - Apply template
5. **View Applied Plan** - Return to home to see applied meals

## Data Flow

```
Admin Creates/Updates Meal Plan
           ↓
Database Trigger Creates Notification
           ↓
Sync Service Processes Notification
           ↓
User App Fetches Templates
           ↓
User Applies Template
           ↓
Template Applied to User's Meal Plan
```

## Meal Plan Structure

### Admin Meal Plan Format

```json
{
  "id": 1,
  "name": "7-Day Mediterranean Plan",
  "description": "Healthy Mediterranean diet...",
  "week_start": "2024-01-01",
  "status": "active",
  "meals": {
    "Monday": {
      "Breakfast": {
        "recipe_name": "Greek Yogurt with Berries",
        "servings": 1,
        "image": "🥣"
      },
      "Lunch": {
        "recipe_name": "Mediterranean Salad",
        "servings": 1,
        "image": "🥗"
      }
    }
  }
}
```

### User Meal Plan Entry

```json
{
  "user_id": "user-123",
  "week": "Week - 1",
  "day": "Monday",
  "meal_type": "Breakfast",
  "recipe_name": "Greek Yogurt with Berries",
  "is_admin_generated": true,
  "admin_meal_plan_id": 1
}
```

## Sync Notifications

The system uses database triggers to automatically create notifications when admin meal plans change:

- **Create**: New meal plan available
- **Update**: Existing meal plan modified
- **Delete**: Meal plan removed

Users can check for updates and apply new templates as they become available.

## Error Handling

- **Offline Mode**: Apps work with cached data when backend is unavailable
- **Fallback Data**: Sample templates shown if sync fails
- **Graceful Degradation**: Core meal planning works without sync
- **User Feedback**: Clear error messages and success notifications

## Security

- **Admin Authentication**: Only authenticated admins can create meal plans
- **User Authentication**: Only authenticated users can apply templates
- **Data Validation**: All meal plan data is validated before storage
- **Permission Checks**: Proper authorization for all operations

## Future Enhancements

- **Real-time Updates**: WebSocket-based real-time sync
- **Template Categories**: Organize templates by diet type, duration, etc.
- **User Ratings**: Allow users to rate and review templates
- **Custom Templates**: Let users create and share their own templates
- **Nutritional Info**: Add nutritional data to meal plans
- **Shopping Lists**: Generate shopping lists from applied templates

## Troubleshooting

### Common Issues

1. **Templates Not Loading**
   - Check backend connectivity
   - Verify authentication token
   - Check browser console for errors

2. **Sync Not Working**
   - Ensure both backends are running
   - Check database triggers are active
   - Verify meal plan status is "active"

3. **Template Application Fails**
   - Check user authentication
   - Verify target week selection
   - Check for conflicting meals

### Debug Mode

Enable debug logging in backend:

```python
logging.basicConfig(level=logging.DEBUG)
```

Check sync notifications:

```sql
SELECT * FROM meal_plan_notifications ORDER BY timestamp DESC LIMIT 10;
```

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review backend logs
3. Verify database schema is up to date
4. Test with sample data first