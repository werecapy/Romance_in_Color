import requests
from bs4 import BeautifulSoup
import json

# URL of the book page
url = "https://www.romance.io/books/671776d0033e20e3197d5753/cruel-winter-with-you-ali-hazelwood"

# Fetch the page content
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Extract title
title = soup.find('title').text.strip()

# Extract author
author = soup.find('a', {'@id': 'https://www.romance.io/authors/6131cdc208b4d93114f22ef6/ali-hazelwood'}).text.strip()

# Extract the JSON-LD script to get additional details
json_data = soup.find('script', type='application/ld+json').text.strip()
book_data = json.loads(json_data)

# Extract rating
rating = book_data[0]['aggregateRating']['ratingValue']

# Extract steam level
description = book_data[0]['description']
steam_level_start = description.find("Spice/Steam/Heat level:")
steam_level_end = description.find("stars", steam_level_start)
steam_level = description[steam_level_start:steam_level_end].split(":")[1].strip()

# Extract date published
date_published = book_data[0]['datePublished']

# Extract cover image URL
cover_image_url = book_data[0]['image']

# Extract tags
tags_start = description.find("is tagged as")
tags = description[tags_start:].split(" - ")[1]
tags_list = tags.split(", ")

# Output extracted information
book_info = {
    'title': title,
    'author': author,
    'rating': rating,
    'steam_level': steam_level,
    'date_published': date_published,
    'cover_image_url': cover_image_url,
    'tags': tags_list
}

print(book_info)
