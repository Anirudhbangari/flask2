from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

app = Flask(__name__)

# Scraping Amazon with retry logic, error handling, and proxy option
def scrape_amazon():
    url = 'https://www.amazon.com/s?k=smartphone'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    # Optional: Add proxy (if you need to rotate IPs to avoid being blocked)
    proxies = {
        # 'http': 'http://your-proxy-url:port',
        # 'https': 'https://your-proxy-url:port'
    }

    # Setting up retry logic
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    try:
        # Fetching the Amazon page
        response = session.get(url, headers=headers, proxies=proxies, timeout=10)
        response.raise_for_status()

        # Log the raw HTML for troubleshooting
        print("Raw HTML content:", response.text[:500])  # Only print the first 500 characters

        # Parsing the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        items = []
        for product in soup.find_all('div', {'data-component-type': 's-search-result'}):
            name = product.h2.text.strip()
            price = product.find('span', 'a-price')
            if price:
                price = price.text.strip()
            else:
                price = 'Unavailable'
            items.append({'name': name, 'price': price})

        print("Amazon Items:", items)  # Print scraped data to console for testing
        return items

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Amazon: {e}")
        return []

@app.route('/')
def home():
    # Scrape Amazon data
    amazon_items = scrape_amazon()

    return render_template('index1.html', amazon_items=amazon_items)

# Flask will run on debug mode
if __name__ == '__main__':
    app.run(debug=True)

