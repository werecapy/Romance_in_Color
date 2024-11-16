import requests
from bs4 import BeautifulSoup
import json

# URL to scrape
url = "https://www.romance.io/books/647f5ec33d6576c079aaa994/iron-flame-rebecca-yarros"

# Send a request to the webpage
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find the <script> tag that contains the JSON-LD data
json_ld_script = soup.find('script', type='application/ld+json')

# Check if the JSON-LD script is found
if json_ld_script:
    try:
        # Parse the JSON data from the script
        json_data = json.loads(json_ld_script.string)

        # Extract author name from the JSON-LD data
        if '@graph' in json_data:
            for item in json_data['@graph']:
                if '@type' in item and item['@type'] == 'Book' and 'author' in item:
                    # Extracting the author's name
                    author_name = item['author'][0]['name']
                    print(f"Author: {author_name}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON-LD: {e}")
else:
    print("No JSON-LD script found on the page.")
