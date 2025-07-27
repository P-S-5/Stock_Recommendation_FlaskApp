from flask import Flask, jsonify
import sqlite3
import subprocess

app = Flask(__name__)

# Function to connect to the SQLite database


def connect_db():
    conn = sqlite3.connect(
        r"C:\Users\Piyush\Documents\Bnp_Hack-15\News-scrapper\sqlite\stock_sentiment_analysis.db")
    return conn

# Function to get all stock_id, ticker_name from the Stock table  


def get_ticker_names():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT stock_id, ticker_name FROM Stock;")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Function to update sentiment for a stock in the Sentiment table


def update_sentiment(stock_id, sentiment):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Sentiment SET sentiment = ? WHERE stock_id = ?", (sentiment, stock_id))
    conn.commit()
    conn.close()

# Function to fetch sentiment from the external scraper (api-returns.py)


def fetch_sentiment_from_scraper(ticker_name):
    try:
        # Run the api-returns.py script with the ticker_name as argument
        result = subprocess.run(
            ['python', r'C:\Users\Piyush\Documents\Bnp_Hack-15\News-scrapper\scripts\api-returns.py', ticker_name], capture_output=True, text=True)
        sentiment = result.stdout.strip()  # Capture the sentiment printed by the script
        return sentiment
    except Exception as e:
        print(f"Error fetching sentiment for {ticker_name}: {e}")
        return None

# Route to fetch all tickers and update sentiments


@app.route('/update_sentiments', methods=['GET'])
def update_all_sentiments():
    tickers = get_ticker_names()  # Get all tickers from the Stock table

    for stock_id, ticker_name in tickers:
        sentiment = fetch_sentiment_from_scraper(
            ticker_name)  # Get sentiment for each ticker
        if sentiment:
            # Update the Sentiment table with the fetched sentiment
            update_sentiment(stock_id, sentiment)
            print(
                f"Updated sentiment for {ticker_name} with sentiment: {sentiment}")
        else:
            print(f"Failed to fetch sentiment for {ticker_name}")

    return jsonify({"message": "Sentiments updated successfully for all tickers."})


if __name__ == "__main__":
    app.run(debug=True)
