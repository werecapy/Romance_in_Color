import requests
from bs4 import BeautifulSoup
import re  # To use regular expressions for extracting data
import json  # Import the json module

# URL of the book page
url = "https://www.romance.io/books/646f27216a90d4b8cc3f74c0/princes-of-ash-angel-lawson-samantha-rue"

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

# Extract the JSON-LD script to get additional details
json_data = soup.find('script', type='application/ld+json').text.strip()

# Load the JSON data
try:
    book_data = json.loads(json_data)
    # Check if the data contains the required author field
    if isinstance(book_data, list) and len(book_data) > 0:
        # Extract author from JSON-LD data
        author_name = book_data[0].get('author', [{}])[0].get('name', 'Author not found')
    else:
        author_name = 'Author not found'
except json.JSONDecodeError:
    print("Error decoding JSON data.")
    author_name = 'Author not found'

# Extract date published (directly from the JSON-LD)
date_published = book_data[0].get('datePublished', 'Date not found')  # Should be in "12 Nov 2024" format

# Extract cover image URL
cover_image_url = book_data[0].get('image', 'No image found')

# Extract tags (if any)
description = book_data[0].get('description', '')
tags_start = description.find("is tagged as")
tags = description[tags_start:].split(" - ")[1] if tags_start != -1 else ''
tags_list = tags.split(", ") if tags else []

# Output extracted information
book_info = {
    'title': title,
    'author': author_name,  # Use the author extracted from JSON-LD
    'rating': rating,
    'spice_level': spice_level,
    'date_published': date_published,
    'cover_image_url': cover_image_url,
    'tags': tags_list
}

print(book_info)
