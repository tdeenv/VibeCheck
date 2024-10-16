# Imports
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

# Accessing unexposed environment variables
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
url_1 = os.getenv("url_1") 

# Function to scrape article links from the provided URL
def scrape_article_links(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    soup = BeautifulSoup(response.text, 'html.parser')

    article_links = []
    for link in soup.find_all('a', attrs={'data-testid': 'article-link'}):
        article_links.append(link['href'])  # Collect the href attribute

    return article_links

# Main script execution
if __name__ == "__main__":
    article_links = scrape_article_links(url_1)

    # Display the collected article links
    for link in article_links:
        print(link)