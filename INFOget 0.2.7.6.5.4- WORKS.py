import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from bs4 import BeautifulSoup
import re
import json
import time

# Function to clean up extracted lists (removes unwanted characters and extra spaces)
def clean_list(lst):
    return [item.strip().replace('\n', '').replace('  ', ' ') for item in lst if item.strip()]

# Set up Google Sheets credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/lizkoempel/Documents/subgenreincolor-c0bb73e9b81b.json', scope)
client = gspread.authorize(creds)

# Open the Google Sheet with URLs
url_sheet = client.open_by_key('1rUaqs21KDwiYbG-6wISvdjFmpmt9Lzu7DuntQ8ZMe-E').worksheet('URLs')
urls = url_sheet.col_values(1)  # Assuming URLs are in the first column


# Function to fetch URLs from a specific column
def fetch_urls_from_column(start_column):
    """
    Fetches URLs from a specific column in the Google Sheet.

    :param start_column: The column number (1-based) from which to fetch the URLs.
    :return: A list of URLs from the specified column.
    """
    # Fetch all values from the specified column
    urls = url_sheet.col_values("1")
    return urls

# List to store already processed URLs
processed_urls = set()

# Function to check for duplicate URLs
def is_duplicate(url):
    if url in processed_urls:
        return True
    else:
        processed_urls.add(url)
        return False

# Function to create header row in the Google Sheet
def create_header(spreadsheet_name, worksheet_name):
    try:
        # Open the main spreadsheet and worksheet
        spreadsheet = client.open("Romance in Color")
        worksheet = spreadsheet.worksheet("pages")

        # Define headers for the columns
        headers = [
            'Title', 'Author', 'Rating', 'Spice Level', 'Date Published',
            'Cover Image URL', 'Tags', 'Content Warnings'
        ]

        # Check if the header is already present
        current_headers = worksheet.row_values(1)
        if not current_headers:  # If there are no headers, write them
            worksheet.append_row(headers)
            print("Headers written to the worksheet.")
        else:
            print("Headers already exist.")
    except Exception as e:
        print(f"An error occurred while creating headers: {e}")
# Function to scrape cover urls
# Function to extract the book cover URL
def get_book_cover(soup):
    # Find the div with the class 'book-cover-container'
    cover_container = soup.find('div', class_='is-hidden-tablet.book-cover-container')

    if cover_container:
        # Extract the src attribute of the <img> tag inside the div
        img_tag = cover_container.find('img')
        if img_tag and img_tag.get('src'):
            return img_tag['src']  # Return the value of the 'src' attribute, which is the image URL
        else:
            return 'No image found'  # Return a placeholder if no <img> tag is found
    else:
        return 'No cover container found'  # Return a placeholder if no cover container is found


# Function to scrape content warnings from the page
def get_content_warnings(soup):
    # Find the div containing the content warnings
    content_warnings_section = soup.find('div', class_='valid-book-topics')

    if content_warnings_section:
        # Extract the list of content warnings from the specific <ul> element with id 'valid-topics-content-warnings'
        content_warnings_list = [
            warning.text.strip() for warning in content_warnings_section.find_all('li', id='valid-topics-content-warnings')
        ]
        # Clean up and return the list of content warnings
        cleaned_content_warnings = clean_list(content_warnings_list)
        return cleaned_content_warnings if cleaned_content_warnings else 'None'  # Return 'None' if no content warnings
    else:
        return 'None'  # Return 'None' if no content warnings section is found

# Function to scrape data from the book URL
def scrape_book_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract title (from the <h1> tag, excluding the series info)
    title_tag = soup.find('h1')
    title = title_tag.text.strip().split('(')[0].strip()  # Removing series info
    author_tag = soup.find('h2', class_='author')
    author_name = author_tag.find('a').text.strip() if author_tag else 'Author not found'

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

    # Extract content warnings using the get_content_warnings function
    content_warnings_list = get_content_warnings(soup)  # Get content warnings from the page

    # Extract the JSON-LD script to get additional details
    json_data = soup.find('script', type='application/ld+json').text.strip()

    # Correctly handle JSON extraction with try-except block
    try:
        book_data = json.loads(json_data)
        print ('Loading json data')
        if isinstance(book_data, dict) and '@graph' in book_data:
            book_details = book_data.get('@graph', [])[0]
            date_published = book_details.get('datePublished', 'Date not found')
            cover_image_url = book_details.get('image', 'No image found')
            print ('Data Found')
        else:
            date_published = 'Date not found'
            print ('data not found')
    except json.JSONDecodeError:
        print("Error decoding JSON data.")
        cover_image_url = None
        date_published = 'Date not found'



    return {
        'title': title,
        'author': author_name,  # Use the author extracted from JSON-LD
        'rating': rating,
        'spice_level': spice_level,
        'date_published': date_published,
        'cover_image_url': cover_image_url,
        'tags': tags_list,  # Tags extracted from the <li> elements
        'content_warnings': content_warnings_list  # Content warnings extracted
    }

# Function to write the data to the main Google Sheet
def write_to_google_sheets(book_info, spreadsheet_name, worksheet_name):
    try:
        # Open the main spreadsheet and worksheet
        spreadsheet = client.open("Romance in Color")
        worksheet = spreadsheet.worksheet("pages")

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



# Loop through each URL and scrape the data with a cooldown of 8 seconds
for url in urls:
    if is_duplicate(url):
        print(f"Skipping duplicate URL: {url}")
        continue  # Skip to the next URL if it's a duplicate

    print(f"Scraping data from URL: {url}")
    book_info = scrape_book_data(url)
    write_to_google_sheets(book_info, "Romance Books", "Book Details")

    # Add a cooldown of 8 seconds between requests
    print("Cooldown... waiting for 8 seconds.")
    time.sleep(8)  # Pause the script for 8 seconds
