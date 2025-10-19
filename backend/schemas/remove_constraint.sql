-- Remove the unique constraint that prevents proper week isolation
DROP INDEX IF EXISTS idx_meal_plans_unique_week_slot;

-- Verify the constraint is removed
SELECT indexname 
FROM pg_indexes 
WHERE tablename = 'meal_plans' 
AND indexname = 'idx_meal_plans_unique_week_slot';