# Meal Planning Backend API

## Project Structure

```
backend/
├── app.py                 # Original monolithic application
├── app_structured.py      # New structured application
├── config/               # Configuration files
│   ├── database.py       # Database connection setup
│   └── settings.py       # Application settings
├── controllers/          # Business logic controllers
│   ├── auth_controller.py
│   ├── recipe_controller.py
│   ├── meal_plan_controller.py
│   └── admin_controller.py
├── models/              # Data models
│   ├── user.py
│   ├── recipe.py
│   ├── meal_plan.py
│   └── subscription.py
├── routes/              # API route definitions
│   ├── auth_routes.py
│   ├── recipe_routes.py
│   ├── meal_plan_routes.py
│   └── admin_routes.py
├── utils/               # Utility functions
│   ├── auth.py          # Authentication helpers
│   ├── analytics.py     # Analytics tracking
│   └── validators.py    # Input validation
└── requirements.txt     # Python dependencies
```

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Run the application:
   ```bash
   python app_structured.py
   ```

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/verify` - Token verification

### Recipes
- `GET /api/recipes` - Get user recipes
- `POST /api/recipes` - Create recipe
- `PUT /api/recipes/{id}` - Update recipe
- `DELETE /api/recipes/{id}` - Delete recipe

### Meal Plans
- `GET /api/meal-plans` - Get meal plans
- `POST /api/meal-plans` - Create meal plan
- `GET /api/meal-plans/admin-templates` - Get admin templates

### Admin
- `POST /api/admin/auth/login` - Admin login
- `GET /api/admin/users` - Get all users
- `GET /api/admin/meal-plans` - Admin meal plans
- `GET /api/admin/recipes` - Admin recipes

## Development Guidelines

1. **Controllers**: Handle business logic and data processing
2. **Models**: Define data structures and database operations
3. **Routes**: Define API endpoints and route requests to controllers
4. **Utils**: Reusable utility functions and helpers
5. **Config**: Application configuration and settings

## Migration from Monolithic

The original `app.py` contains all functionality in a single file. The new structure separates concerns for better maintainability. Both files can run simultaneously during migration.