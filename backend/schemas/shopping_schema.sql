-- Create shopping_items table for storing user's shopping items
CREATE TABLE shopping_items (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    quantity INTEGER DEFAULT 1,
    unit VARCHAR(50),
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster user lookups
CREATE INDEX idx_shopping_items_user_id ON shopping_items(user_id);
CREATE INDEX idx_shopping_items_created_at ON shopping_items(created_at DESC);

-- Create recent_items table for frequently added items
CREATE TABLE recent_items (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    frequency INTEGER DEFAULT 1,
    last_used TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create unique constraint to prevent duplicate recent items per user
CREATE UNIQUE INDEX idx_recent_items_user_item ON recent_items(user_id, LOWER(item_name));

-- Create index for faster recent items lookup
CREATE INDEX idx_recent_items_user_frequency ON recent_items(user_id, frequency DESC, last_used DESC);