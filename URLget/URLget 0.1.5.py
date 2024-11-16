import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time


def generate_weekly_url(base_url, date_str):
    """
    Generates a URL for a specific week using the base Romance.io URL template.
    """
    return base_url.replace("2022-04-24", date_str)


def fetch_book_links(weekly_url):
    """
    Fetches all book links from the Romance.io weekly new releases page.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"
    }

    response = requests.get(weekly_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch the page for {weekly_url}. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    book_links = []

    # Find all book links in the specific container
    containers = soup.find_all("div", class_="flexbox-not-mobile is-clearfix")
    for container in containers:
        link_tag = container.find("a", href=True)
        if link_tag:
            book_links.append(f"https://www.romance.io{link_tag['href']}")

    return book_links


def automate_weekly_scrape(start_date, base_url, cooldown=5):
    """
    Automates weekly URL generation and scraping, going one week into the past.
    Stops when no links are found for a week.

    Args:
        start_date (str): The starting date in YYYY-MM-DD format.
        base_url (str): The base URL template.
        cooldown (int): Time in seconds to wait between requests.
    """
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    stop_scraping = False

    while not stop_scraping:
        # Format the current date
        formatted_date = current_date.strftime("%Y-%m-%d")
        weekly_url = generate_weekly_url(base_url, formatted_date)

        print(f"\nFetching data for week starting {formatted_date} from: {weekly_url}")

        # Fetch book links
        book_links = fetch_book_links(weekly_url)

        if book_links:
            print(f"Found {len(book_links)} book links for {formatted_date}:")
            for link in book_links:
                print(link)
        else:
            print(f"No book links found for {formatted_date}. Stopping scrape.")
            stop_scraping = True

        # Decrement by one week
        current_date -= timedelta(weeks=1)

        # Wait for cooldown
        if not stop_scraping:
            print(f"Waiting {cooldown} seconds before fetching the next week...")
            time.sleep(cooldown)


if __name__ == "__main__":
    # Base URL template
    base_url = "https://www.romance.io/new/weekly/2022-04-24?showall=true#showall"

    # Start date
    start_date = "2024-11-10"

    # Cooldown time between requests (in seconds)
    cooldown_time = 5

    # Run the automated scraper
    automate_weekly_scrape(start_date, base_url, cooldown=cooldown_time)
