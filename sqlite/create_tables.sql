-- Create the User table
CREATE TABLE User (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-incremented unique identifier for each user
    username TEXT NOT NULL UNIQUE,             -- Username must be unique
    user_password TEXT NOT NULL                -- Password for the user
);

-- Create the Stock table
CREATE TABLE Stock (
    stock_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-incremented unique identifier for each stock
    ticker_name TEXT NOT NULL UNIQUE,           -- Stock ticker name, must be unique
    current_price REAL NOT NULL DEFAULT 0.0     -- Current price of the stock
);

-- Create the Portfolio table
CREATE TABLE Portfolio (
    portfolio_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Auto-incremented unique identifier for portfolio entries
    user_id INTEGER NOT NULL,                       -- Foreign key linking to User
    stock_id INTEGER NOT NULL,                      -- Foreign key linking to Stock
    original_price REAL NOT NULL,                   -- Original purchase price of the stock
    quantity INTEGER NOT NULL,                      -- Quantity of stocks owned
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE, -- Delete portfolio entries if user is deleted
    FOREIGN KEY (stock_id) REFERENCES Stock(stock_id) ON DELETE CASCADE -- Delete portfolio entries if stock is deleted
);

-- Create the Sentiment table
CREATE TABLE Sentiment (
    sentiment_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Auto-incremented unique identifier for sentiments
    stock_id INTEGER NOT NULL,                      -- Foreign key linking to Stock
    sentiment TEXT NOT NULL,                        -- Sentiment data, e.g., "positive", "negative", or "neutral"
    FOREIGN KEY (stock_id) REFERENCES Stock(stock_id) ON DELETE CASCADE -- Delete sentiment if stock is deleted
);
