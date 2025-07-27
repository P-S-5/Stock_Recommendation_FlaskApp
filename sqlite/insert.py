import sqlite3

# Connect to the existing SQLite database
connection = sqlite3.connect("stock_sentiment_analysis.db")
cursor = connection.cursor()

# 1. Insert data into the Stock table
cursor.executemany("""
    INSERT INTO Stock (ticker_name, stock_name, current_price) 
    VALUES (?, ?, ?);
""", [
    ("AAPL", "Apple Inc", 175.0), 
    ("MSFT", "Microsoft Corporation", 300.0), 
    ("AMZN", "Amazon.com, Inc.", 140.0)
])

# 2. Insert data into the User table
cursor.executemany("""
    INSERT INTO User (username, user_password) 
    VALUES (?, ?);
""", [
    ("john_doe", "password123"),
    ("jane_smith", "password456"),
    ("alice_jones", "password789")
])

# 3. Insert data into the Portfolio table
cursor.executemany("""
    INSERT INTO Portfolio (user_id, stock_id, original_price, quantity) 
    VALUES (?, ?, ?, ?);
""", [
    (1, 1, 150.0, 10),  # User 1 owns 10 AAPL at price 150
    (2, 2, 290.0, 5),   # User 2 owns 5 MSFT at price 290
    (3, 3, 130.0, 7)    # User 3 owns 7 AMZN at price 130
])

# 4. Insert data into the Sentiment table
cursor.executemany("""
    INSERT INTO Sentiment (stock_id, sentiment) 
    VALUES (?, ?);
""", [
    (1, "Strong Buy"),  # Sentiment for AAPL
    (2, "Hold"),        # Sentiment for MSFT
    (3, "Sell")         # Sentiment for AMZN
])

# Commit changes and close the connection
connection.commit()
connection.close()

print("Dummy values inserted successfully.")