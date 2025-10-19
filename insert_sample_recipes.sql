-- Insert sample admin recipes
INSERT INTO admin_recipes (title, description, ingredients, instructions, cook_time, servings, difficulty, category, image, author, status, is_admin_recipe) VALUES
('Mediterranean Quinoa Bowl', 'A healthy and delicious quinoa bowl with Mediterranean flavors', 
 '["1 cup quinoa", "2 cups vegetable broth", "1 cucumber diced", "1 cup cherry tomatoes", "1/2 red onion", "1/4 cup olives", "1/4 cup feta cheese", "2 tbsp olive oil", "1 lemon juiced", "Salt and pepper to taste"]',
 '["Rinse quinoa and cook in vegetable broth for 15 minutes", "Let quinoa cool completely", "Dice cucumber, tomatoes, and red onion", "Mix vegetables with quinoa", "Add olives and feta cheese", "Whisk olive oil and lemon juice", "Dress salad and season with salt and pepper", "Serve chilled"]',
 25, 4, 'easy', 'Lunch', '🥗', 'Admin', 'published', true),

('Grilled Salmon with Asparagus', 'Perfectly grilled salmon with roasted asparagus', 
 '["4 salmon fillets", "1 lb asparagus", "2 tbsp olive oil", "2 cloves garlic minced", "1 lemon sliced", "Salt and pepper", "Fresh dill"]',
 '["Preheat grill to medium-high heat", "Trim asparagus ends", "Toss asparagus with olive oil, salt, and pepper", "Season salmon with salt, pepper, and garlic", "Grill salmon 4-5 minutes per side", "Grill asparagus 8-10 minutes", "Serve with lemon slices and fresh dill"]',
 20, 4, 'medium', 'Dinner', '🐟', 'Admin', 'published', true);