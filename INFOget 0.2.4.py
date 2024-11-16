import requests
from bs4 import BeautifulSoup
import json

# URL of the book page
url = "https://www.romance.io/books/647f5ec33d6576c079aaa994/iron-flame-rebecca-yarros"

# Fetch the page content
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Extract title
title = soup.find('title').text.strip()

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

# Extract rating
rating = book_data[0].get('aggregateRating', {}).get('ratingValue', 'Rating not found')

# Extract steam level
description = book_data[0].get('description', '')
steam_level_start = description.find("Spice/Steam/Heat level:")
steam_level_end = description.find("stars", steam_level_start)
steam_level = description[steam_level_start:steam_level_end].split(":")[1].strip() if steam_level_start != -1 else 'Steam level not found'

# Extract date published
date_published = book_data[0].get('datePublished', 'Date not found')

# Extract cover image URL
cover_image_url = book_data[0].get('image', 'No image found')

# Extract tags
tags_start = description.find("is tagged as")
tags = description[tags_start:].split(" - ")[1] if tags_start != -1 else ''
tags_list = tags.split(", ") if tags else []

# Output extracted information
book_info = {
    'title': title,
    'author': author_name,  # Use the author extracted from JSON-LD
    'rating': rating,
    'steam_level': steam_level,
    'date_published': date_published,
    'cover_image_url': cover_image_url,
    'tags': tags_list
}

print(book_info)
