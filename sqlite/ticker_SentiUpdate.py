import sqlite3

# Connect to the database
connection = sqlite3.connect("stock_sentiment_analysis.db")
cursor = connection.cursor()

# Create ticker_Senti table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS ticker_Senti (
        ticker_name TEXT NOT NULL,
        sentiment TEXT NOT NULL
    );
""")

# Insert initial data into ticker_Senti
cursor.execute("""
    INSERT INTO ticker_Senti (ticker_name, sentiment)
    SELECT Stock.ticker_name, Sentiment.sentiment
    FROM Stock
    JOIN Sentiment ON Stock.stock_id = Sentiment.stock_id;
""")

# Create triggers for keeping ticker_Senti updated
cursor.executescript("""
    CREATE TRIGGER IF NOT EXISTS after_stock_insert
    AFTER INSERT ON Stock
    BEGIN
        INSERT INTO ticker_Senti (ticker_name, sentiment)
        SELECT NEW.ticker_name, Sentiment.sentiment
        FROM Sentiment
        WHERE Sentiment.stock_id = NEW.stock_id;
    END;

    CREATE TRIGGER IF NOT EXISTS after_sentiment_insert
    AFTER INSERT ON Sentiment
    BEGIN
        INSERT INTO ticker_Senti (ticker_name, sentiment)
        SELECT Stock.ticker_name, NEW.sentiment
        FROM Stock
        WHERE Stock.stock_id = NEW.stock_id;
    END;

    CREATE TRIGGER IF NOT EXISTS after_stock_update
    AFTER UPDATE ON Stock
    BEGIN
        UPDATE ticker_Senti
        SET ticker_name = NEW.ticker_name
        WHERE ticker_name = OLD.ticker_name;
    END;

    CREATE TRIGGER IF NOT EXISTS after_sentiment_update
    AFTER UPDATE ON Sentiment
    BEGIN
        UPDATE ticker_Senti
        SET sentiment = NEW.sentiment
        WHERE ticker_name IN (
            SELECT ticker_name FROM Stock WHERE Stock.stock_id = NEW.stock_id
        );
    END;

    CREATE TRIGGER IF NOT EXISTS after_stock_delete
    AFTER DELETE ON Stock
    BEGIN
        DELETE FROM ticker_Senti
        WHERE ticker_name = OLD.ticker_name;
    END;

    CREATE TRIGGER IF NOT EXISTS after_sentiment_delete
    AFTER DELETE ON Sentiment
    BEGIN
        DELETE FROM ticker_Senti
        WHERE ticker_name IN (
            SELECT ticker_name FROM Stock WHERE Stock.stock_id = OLD.stock_id
        );
    END;
""")

# Commit and close the connection
connection.commit()
connection.close()

print("ticker_Senti table and triggers created successfully.")
