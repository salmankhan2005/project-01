-- Admin Recipes Table
CREATE TABLE IF NOT EXISTS admin_recipes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    ingredients JSONB DEFAULT '[]',
    instructions JSONB DEFAULT '[]',
    cook_time INTEGER DEFAULT 30,
    servings INTEGER DEFAULT 1,
    difficulty VARCHAR(50) DEFAULT 'medium',
    category VARCHAR(100) DEFAULT 'Main',
    image VARCHAR(255) DEFAULT '🍽️',
    author VARCHAR(255) DEFAULT 'Admin',
    status VARCHAR(50) DEFAULT 'published',
    created_by INTEGER REFERENCES admin_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_admin_recipe BOOLEAN DEFAULT TRUE
);

-- Recipe Notifications Table
CREATE TABLE IF NOT EXISTS recipe_notifications (
    id SERIAL PRIMARY KEY,
    type VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    recipe_id INTEGER,
    recipe_title VARCHAR(255),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    data JSONB DEFAULT '{}',
    processed BOOLEAN DEFAULT FALSE
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_admin_recipes_status ON admin_recipes(status);
CREATE INDEX IF NOT EXISTS idx_admin_recipes_created_at ON admin_recipes(created_at);
CREATE INDEX IF NOT EXISTS idx_recipe_notifications_timestamp ON recipe_notifications(timestamp);
CREATE INDEX IF NOT EXISTS idx_recipe_notifications_processed ON recipe_notifications(processed);

-- Sample admin recipes
INSERT INTO admin_recipes (title, description, ingredients, instructions, cook_time, servings, difficulty, category, image, author, status) VALUES
('Mediterranean Quinoa Bowl', 'A healthy and delicious quinoa bowl with Mediterranean flavors', 
 '["1 cup quinoa", "2 cups vegetable broth", "1 cucumber diced", "1 cup cherry tomatoes", "1/2 red onion", "1/4 cup olives", "1/4 cup feta cheese", "2 tbsp olive oil", "1 lemon juiced", "Salt and pepper to taste"]',
 '["Rinse quinoa and cook in vegetable broth for 15 minutes", "Let quinoa cool completely", "Dice cucumber, tomatoes, and red onion", "Mix vegetables with quinoa", "Add olives and feta cheese", "Whisk olive oil and lemon juice", "Dress salad and season with salt and pepper", "Serve chilled"]',
 25, 4, 'easy', 'Lunch', '🥗', 'Admin', 'published'),

('Grilled Salmon with Asparagus', 'Perfectly grilled salmon with roasted asparagus', 
 '["4 salmon fillets", "1 lb asparagus", "2 tbsp olive oil", "2 cloves garlic minced", "1 lemon sliced", "Salt and pepper", "Fresh dill"]',
 '["Preheat grill to medium-high heat", "Trim asparagus ends", "Toss asparagus with olive oil, salt, and pepper", "Season salmon with salt, pepper, and garlic", "Grill salmon 4-5 minutes per side", "Grill asparagus 8-10 minutes", "Serve with lemon slices and fresh dill"]',
 20, 4, 'medium', 'Dinner', '🐟', 'Admin', 'published'),

('Overnight Oats with Berries', 'Easy make-ahead breakfast with fresh berries', 
 '["1/2 cup rolled oats", "1/2 cup milk", "1 tbsp chia seeds", "1 tbsp honey", "1/4 cup mixed berries", "1 tbsp almond butter", "1/4 tsp vanilla extract"]',
 '["Mix oats, milk, chia seeds, and vanilla in a jar", "Add honey and stir well", "Top with berries and almond butter", "Refrigerate overnight", "Enjoy cold in the morning"]',
 5, 1, 'easy', 'Breakfast', '🥣', 'Admin', 'published');