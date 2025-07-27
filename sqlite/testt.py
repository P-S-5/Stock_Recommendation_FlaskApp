import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('stock_sentiment_analysis.db')
cursor = conn.cursor()

# Get a list of all tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(tables)

# Close the connection
conn.close()
