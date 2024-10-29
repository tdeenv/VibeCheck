# imports
import os
import json
import time
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import openai  

# Load environment variables from .env file
load_dotenv()

# Selecting API key
API_KEY = os.getenv("OPENAI_API_KEY")
url_1 = os.getenv("url_1") 

# Set the API key for OpenAI
openai.api_key = API_KEY

# Define the allowed categories
allowed_categories = [
    "/culture", "/property", "/national", "/business", 
    "/money", "/world", "/technology", "/politics", 
    "/environment", "/education"
]

# Function to scrape article titles, links, and snippets from the provided URL
def scrape_article_info(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    soup = BeautifulSoup(response.text, 'html.parser')

    articles_info = []
    for link in soup.find_all('a', attrs={'data-testid': 'article-link'}):
        title = link.text.strip() 
        
        # Find the corresponding snippet by navigating the DOM
        snippet = link.find_next('p', class_='_3XEsE')
        snippet_text = snippet.text.strip() if snippet else "No snippet available"  # Get the snippet text if exists

        articles_info.append({
            'title': title,
            'snippet': snippet_text  # Save the snippet along with title
        })

    return articles_info

# Function to send a sentiment analysis request to OpenAI API using the openai package
def analyze_sentiment(articles_info):
    combined_text = "\n\n".join(f"Title: {article['title']}\nSnippet: {article['snippet']}" for article in articles_info)

    # Prepare the messages for the API
    messages = [
        {
            "role": "user",
            "content": f"Please analyze the sentiment of the following articles and provide a score for each category: {combined_text}."
        }
    ]

    max_retries = 5
    backoff_factor = 2  # Exponential backoff factor

    for attempt in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            return response['choices'][0]['message']['content']  # Adjusted to get content from the response
        except openai.error.RateLimitError:
            wait_time = backoff_factor ** attempt  # Exponential backoff
            print(f"Rate limit hit. Waiting for {wait_time} seconds before retrying...")
            time.sleep(wait_time)  # Wait before retrying
            continue  # Retry the request
        except Exception as e:
            print(f"An error occurred: {e}")
            break  # Break the loop for other types of errors

    raise Exception("Max retries exceeded for API request.")

# Function to filter sentiment results
def filter_results(sentiment_results):
    filtered_results = []

    # Loop through each result and filter based on allowed categories
    for category in sentiment_results.split('\n'):  # Adjust based on the actual format of the results
        if any(cat in category for cat in allowed_categories):
            filtered_results.append(category)  # Keep only allowed categories

    return filtered_results

# Main script execution
if __name__ == "__main__":
    # Scrape titles and snippets from url_1 and save to a variable
    articles_info_1 = scrape_article_info(url_1)

    # Send the JSON data to OpenAI API for sentiment analysis
    sentiment_results = analyze_sentiment(articles_info_1)

    # Filter the results to remove links and unwanted categories
    filtered_sentiment_results = filter_results(sentiment_results)

    # Save the filtered results to a JSON file
    with open('filtered_sentiment_results.json', 'w') as json_file:
        json.dump(filtered_sentiment_results, json_file, indent=4)

    # Display the filtered sentiment analysis results
    print("Filtered Sentiment Analysis Results:")
    print(json.dumps(filtered_sentiment_results, indent=4))
