import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from bs4 import BeautifulSoup
import re
import json

# Set up Google Sheets credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/lizkoempel/Documents/subgenreincolor-c0bb73e9b81b.json', scope)
client = gspread.authorize(creds)

# Open the Google Sheet with URLs
url_sheet = client.open_by_key('your_spreadsheet_key_here').worksheet('URLs')
urls = url_sheet.col_values(1)  # Assuming URLs are in the first column

# Function to scrape data from the book URL
def scrape_book_data(url):
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

    try:
        book_data = json.loads(json_data)
        if isinstance(book_data, dict) and '@graph' in book_data:
            book_details = book_data.get('@graph', [])[0]
            author_name = book_details.get('author', [{}])[0].get('name', 'Author not found')
            date_published = book_details.get('datePublished', 'Date not found')
        else:
            author_name = 'Author not found'
            date_published = 'Date not found'
    except json.JSONDecodeError:
        print("Error decoding JSON data.")
        author_name = 'Author not found'
        date_published = 'Date not found'

    cover_image_url = book_details.get('image', 'No image found')

    return {
        'title': title,
        'author': author_name,
        'rating': rating,
        'spice_level': spice_level,
        'date_published': date_published,
        'cover_image_url': cover_image_url,
        'tags': tags_list,
        'content_warnings': content_warnings_list
    }

# Function to write the data to the main Google Sheet
def write_to_google_sheets(book_info, spreadsheet_name, worksheet_name):
    try:
        # Open the main spreadsheet and worksheet
        spreadsheet = client.open(spreadsheet_name)
        worksheet = spreadsheet.worksheet(worksheet_name)

        # Prepare data for writing
        row = [
            book_info['title'],
            book_info['author'],
            book_info['rating'],
            book_info['spice_level'],
            book_info['date_published'],
            book_info['cover_image_url'],
            ", ".join(book_info['tags']),
            ", ".join(book_info['content_warnings'])
        ]

        # Append data to the worksheet
        worksheet.append_row(row)
        print(f"Data written for book: {book_info['title']}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Loop through each URL and scrape the data
for url in urls:
    print(f"Scraping data from URL: {url}")
    book_info = scrape_book_data(url)
    write_to_google_sheets(book_info, "Romance Books", "Book Details")
