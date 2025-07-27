import finnhub
import logging
import os
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
import json
from newspaper import Article
import re
from transformers import pipeline
import ast
import sys

load_dotenv()

today = datetime.today().date()
yesterday = today - timedelta(days=1)
ticker_name = "MSFT"

ticker_name = sys.argv[1]  # Get the ticker_name passed from Flask

def scrape_content(url):
    """
    Extract only the main text content from a webpage.

    Args:
        url (str): The URL of the webpage to scrape

    Returns:
        str: Main text content of the webpage
    """
    try:
        # First attempt using newspaper3k
        article = Article(url)
        article.download()
        article.parse()

        text = article.text

        # If newspaper3k doesn't get good content, fall back to custom extraction
        if not text.strip():
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'iframe']):
                element.decompose()

            # Try to find main content container
            main_content = None
            potential_containers = soup.find_all(['article', 'main', 'div'],
                                                 class_=re.compile(r'(article|post|content|story)', re.I))

            if potential_containers:
                main_content = max(potential_containers,
                                   key=lambda x: len(x.get_text(strip=True)))

            if main_content:
                text = main_content.get_text()

        # Clean up the text
        text = re.sub(r'\s+', ' ', text).strip()  # Remove extra whitespace
        text = re.sub(
            r'Share\s*(on|via)\s*(Facebook|Twitter|LinkedIn|Email)', '', text, flags=re.I)
        text = re.sub(r'Related\s*Articles?', '', text, flags=re.I)
        text = re.sub(r'Comments?', '', text, flags=re.I)
        text = re.sub(r'\[\s*\d+\s*\]', '', text)  # Remove reference numbers

        return text

    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        return None


# Load the input JSON data from a file
def load_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


# Save the extracted text to a text file
def save_text_to_file(text_list, output_file_path):
    with open(output_file_path, 'w') as file:
        file.write(', '.join(text_list))


def chunk_text(text, chunk_size):
    """
    Split text into chunks of a specified size.
    """
    words = text.split()  # Split the text into words
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i + chunk_size])


def fetch_company_news(api_key, symbol, start_date, end_date):
    try:
        # Initialize Finnhub client
        finnhub_client = finnhub.Client(api_key=api_key)

        # Fetch company news
        news = finnhub_client.company_news(
            symbol, _from=start_date, to=end_date)
        logging.info(
            f"Fetched {len(news)} news articles for {symbol} from {start_date} to {end_date}.")
        return news

    except Exception as e:
        logging.error(f"Error fetching news for {symbol}: {e}")
        return []


def save_to_json_file(data, filename):
    try:
        with open(filename, "w") as json_file:
            json.dump(data, json_file, indent=4)
        logging.info(f"Data saved to {filename}")
    except Exception as e:
        logging.error(f"Error saving data to {filename}: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    # Example usage
    API_KEY = os.getenv("API_KEY")

    if not API_KEY:
        raise ValueError("API key is missing. Check your .env file.")

    # Fetch news for Apple Inc. between specific dates
    symbol = ticker_name
    # start_date = yesterday.strftime("%Y-%m-%d")
    # end_date = today.strftime("%Y-%m-%d")
    start_date = yesterday.strftime("%Y-%m-%d") 
    end_date = today.strftime("%Y-%m-%d")
    news = fetch_company_news(API_KEY, symbol, start_date, end_date)

    save_to_json_file(
        news, r"C:\Users\Piyush\Documents\Bnp_Hack-15\News-scrapper\data\raw-news.json")
    # print("News saved to raw-news.json")

    input_file_path = r'C:\Users\Piyush\Documents\Bnp_Hack-15\News-scrapper\data\raw-news.json'
    output_file_path = r'C:\Users\Piyush\Documents\Bnp_Hack-15\News-scrapper\data\scraped_with_sentiment.txt'
    model_path = r"C:\Users\Piyush\Documents\Bnp_Hack-15\News-scrapper\models"

    # Load the JSON data
    news_data = load_json_file(input_file_path)

    # Slice the list to get only the top 10 articles
    top_10_articles = news_data[:10]

    # Initialize the sentiment analysis pipeline
    pipe = pipeline("text-classification", model=model_path,
                    device=0, truncation=True, max_length=512)

    # List to hold the results
    sentiment_results = []

    for article in top_10_articles:
        url = article['url']
        # print(f"Scraping URL: {url}")

        # Scrape the article's text
        article_text = scrape_content(url)

        if article_text:
            # Perform sentiment analysis on the scraped text
            sentiment = pipe(article_text)

            # Store the URL, text snippet, and sentiment result
            sentiment_results.append(sentiment)

    # print(sentiment_results)
    # Save the results to a file
    with open(output_file_path, 'w', encoding='utf-8') as f:
        for sentiments in sentiment_results:
            for sentiment in sentiments:  # If storing multiple chunks, iterate through each sentiment
                f.write(f"{sentiment}\n")  # Write each sentiment on a new line

    label_weights = {
        "positive": 1.5,
        "neutral": 1,
        "negative": 0.5
    }
    # Calculate weighted average
    total_score = 0
    total_weight = 0
    for item in sentiment_results:
        for sentiment in item:
            label = sentiment['label']
            score = sentiment['score']
            weight = label_weights[label]
            total_score += weight * score
            total_weight += score

    # Avoid division by zero
    if total_weight > 0:
        weighted_average = total_score / total_weight
    else:
        weighted_average = 0

    # Map the weighted average to a category
    if weighted_average > 0.85:
        category = "Strong Buy"
    elif 0.75 < weighted_average <= 0.85:
        category = "Buy"
    elif 0.5 <= weighted_average <= 0.75:
        category = "Hold"
    elif 0.35 <= weighted_average < 0.5:
        category = "Sell"
    else:
        category = "Strong Sell"

    # print(f"Weighted Average: {weighted_average:.2f}")
    print(category)
    # print(f"Sentiment analysis results saved to {output_file_path}")