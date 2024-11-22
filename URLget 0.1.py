import requests
from bs4 import BeautifulSoup
import datetime
import time
import gspread
from google.oauth2.service_account import Credentials


def scrape_romance_io_weekly(url):
    """
    Scrapes book links from the Romance.io weekly new releases page.

    Args:
        url (str): The URL of the weekly new releases page.

    Returns:
        list: A list of book URLs.
    """
    try:
        print(f"Fetching data from: {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        book_links = []
        link_count = 0  # Track the number of links fetched

        for a in soup.select(".flexbox-not-mobile a.col"):
            book_link = f"https://www.romance.io{a['href']}"
            book_links.append(book_link)
            link_count += 1
            print(f"Fetched URL: {book_link}")

            # After every 50 links, add a 15-second cooldown
            if link_count % 50 == 0:
                print("Fetched 50 links, waiting 15 seconds...")
                time.sleep(15)

        return book_links
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return []


def append_to_google_sheet(sheet_id, book_links):
    """
    Appends a list of book URLs to the Google Sheet without duplicates.

    Args:
        sheet_id (str): The ID of the Google Sheet.
        book_links (list): List of URLs to append.
    """
    try:
        # Define the scope and authenticate
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        credentials = Credentials.from_service_account_file(
            "/Users/lizkoempel/Documents/subgenreincolor-c0bb73e9b81b.json", scopes=SCOPES)
        client = gspread.authorize(credentials)

        # Access the spreadsheet
        sheet = client.open_by_key("1rUaqs21KDwiYbG-6wISvdjFmpmt9Lzu7DuntQ8ZMe-E").sheet1

        # Get existing URLs from the sheet to avoid duplicates
        existing_urls = {row[0] for row in sheet.get_all_values()}

        # Filter out URLs that are already in the sheet
        new_urls = [url for url in book_links if url not in existing_urls]

        # Check if sheet is empty and add the header if necessary
        if sheet.row_count == 0:
            print("Sheet is empty. Adding header row.")
            sheet.append_row(["URL"])  # Add header to the first row

        # Append new URLs in batches of 50
        for i in range(0, len(new_urls), 50):
            batch = new_urls[i:i + 50]
            sheet.append_rows([[url] for url in batch])
            print(f"Successfully added {len(batch)} URLs to the Google Sheet.")

            # Pause for 10 seconds after every 50 URLs
            print("Waiting 10 seconds before the next batch...")
            time.sleep(10)

        print(f"Successfully added {len(new_urls)} new URLs to the Google Sheet.")
    except Exception as e:
        print(f"Error appending to Google Sheet: {e}")
        # If there's an issue, sleep for a while before retrying
        time.sleep(30)
        append_to_google_sheet(sheet_id, book_links)


def automate_weekly_scrape(start_date, base_url, sheet_id):
    """
    Automatically scrape weekly book links and add them to a Google Sheet.

    Args:
        start_date (str): The starting date in YYYY-MM-DD format.
        base_url (str): The base URL with the date placeholder.
        sheet_id (str): The ID of the Google Sheet.
    """
    current_date = start_date
    while True:
        print(f"Fetching data for week starting {current_date}...")
        url = base_url.replace("2024-11-10", current_date)
        book_links = scrape_romance_io_weekly(url)

        if not book_links:  # Stop if no book links are found
            print(f"No data found for {current_date}. Ending scrape.")
            break

        print(f"Found {len(book_links)} book links for {current_date}. Adding to Google Sheet...")
        append_to_google_sheet(sheet_id, book_links)

        # Cooldown after processing each week's data
        print(f"Waiting 20 seconds before fetching the next week's data...")
        time.sleep(40)  # Cooldown between different dates

        # Subtract one week for the next iteration
        current_date = (datetime.datetime.strptime(current_date, "%Y-%m-%d") - datetime.timedelta(weeks=1)).strftime(
            "%Y-%m-%d")


# Set up the script parameters
if __name__ == "__main__":
    start_date = "2022-05-29"  # Start scraping from this date
    base_url = "https://www.romance.io/new/weekly/2024-11-10?showall=true#showall"  # Base URL template
    sheet_id = "1rUaqs21KDwiYbG-6wISvdjFmpmt9Lzu7DuntQ8ZMe-E"  # Your Google Sheet ID

    automate_weekly_scrape(start_date, base_url, sheet_id)
