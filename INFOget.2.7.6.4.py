import requests
from bs4 import BeautifulSoup
import re
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Function to clean up extracted lists (removes unwanted characters and extra spaces)
def clean_list(lst):
    return [item.strip().replace('\n', '').replace('  ', ' ') for item in lst if item.strip()]

# URL of the book page
url = "https://www.romance.io/books/647f5ec33d6576c079aaa994/iron-flame-rebecca-yarros"

# Fetch the page content
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Extract title (from the <h1> tag)
title_tag = soup.find('h1')
title = title_tag.text.strip().split('(')[0].strip()  # Remove series info and extra spaces

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
tags_list = clean_list(tags_list)  # Clean up tags

# Extract content warnings
content_warnings_list = [warning.text.strip() for warning in soup.find_all('li', class_='tagged-topic') if 'abuse' in warning.text.lower() or 'death' in warning.text.lower() or 'trauma' in warning.text.lower()]
content_warnings_list = clean_list(content_warnings_list)  # Clean up content warnings

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

# Function to write the data to Google Sheets
def write_to_google_sheets(data, spreadsheet_name, worksheet_name):
    """
    Writes extracted book data to Google Sheets.
    """
    try:
        # Google Sheets API setup
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/lizkoempel/Documents/subgenreincolor-c0bb73e9b81b.json', scope)
        client = gspread.authorize(creds)

        # Open the spreadsheet and worksheet
        spreadsheet = client.open_by_key("1rUaqs21KDwiYbG-6wISvdjFmpmt9Lzu7DuntQ8ZMe-E")
        worksheet = spreadsheet.worksheet("pages")

        # Prepare data for writing
        row = [
            data['title'],
            data['author'],
            data['rating'],
            data['spice_level'],
            data['date_published'],
            data['cover_image_url'],
            ", ".join(data['tags']),
            ", ".join(data['content_warnings'])
        ]

        # Append data to the worksheet
        worksheet.append_row(row)
        print(f"Data written successfully to {worksheet_name} in {spreadsheet_name}.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage of the function
write_to_google_sheets(book_info, "Romance Books", "Book Details")
