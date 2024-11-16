import requests
from bs4 import BeautifulSoup
import re  # To use regular expressions for extracting data
import json  # Import the json module

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

# Extract the tags from the description after "is tagged as"
tags_start = meta_description.find("is tagged as")
tags = meta_description[tags_start:].split(" - ")[1] if tags_start != -1 else ''
tags_list = [tag.strip() for tag in tags.split(",")] if tags else []

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
    'tags': tags_list  # Tags extracted from the description
}

print(book_info)
