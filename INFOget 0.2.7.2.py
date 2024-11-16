import requests
from bs4 import BeautifulSoup
import re  # For regular expressions
import json  # For handling JSON data

# URL of the book page
url = "https://www.romance.io/books/647f5ec33d6576c079aaa994/iron-flame-rebecca-yarros"

# Fetch the page content
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Extract title
title = soup.find('title').text.strip()

# Extract the meta description content
meta_description = soup.find('meta', {'name': 'description'}).get('content', '')

# Use regex to extract the rating
rating_match = re.search(r"Rated (\d+\.\d)/5 stars", meta_description)
rating = rating_match.group(1) if rating_match else 'Rating not found'

# Use regex to extract the spice level
spice_level_match = re.search(r"Spice/Steam/Heat level: (\d)/5", meta_description)
spice_level = spice_level_match.group(1) if spice_level_match else 'Spice level not found'

# Extract the tags from the page
tags_list = [tag.text.strip() for tag in soup.find_all('li', class_='tagged-topic')]

# Extract content warnings (using the <li> tags associated with content warnings)
content_warnings_list = [warning.text.strip() for warning in soup.find_all('li', class_='tagged-topic') if 'abuse' in warning.text.lower() or 'death' in warning.text.lower() or 'trauma' in warning.text.lower()]

# Extract the JSON-LD script to get additional details
json_data = soup.find('script', type='application/ld+json').text.strip()

# Load the JSON data
try:
    book_data = json.loads(json_data)
    # Check if the data contains the required author field
    if isinstance(book_data, dict) and '@graph' in book_data:
        book_details = book_data.get('@graph', [])[0]
        # Extract author from JSON-LD data
        author_name = book_details.get('author', [{}])[0].get('name', 'Author not found')
        # Extract date published from JSON-LD
        date_published = book_details.get('datePublished', 'Date not found')
    else:
        author_name = 'Author not found'
        date_published = 'Date not found'
except json.JSONDecodeError:
    print("Error decoding JSON data.")
    author_name = 'Author not found'
    date_published = 'Date not found'

# Extract cover image URL
cover_image_url = book_details.get('image', 'No image found')

# Output extracted information
book_info = {
    'title': title,
    'author': author_name,  # Use the author extracted from JSON-LD
    'rating': rating,
    'spice_level': spice_level,
    'date_published': date_published,
    'cover_image_url': cover_image_url,
    'tags': tags_list,  # Tags extracted from the <li> elements
    'content_warnings': content_warnings_list  # Content warnings extracted
}

print(book_info)
