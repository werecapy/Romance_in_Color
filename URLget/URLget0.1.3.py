import requests
from bs4 import BeautifulSoup

# URL of the Romance.io new releases page
URL = "https://romance.io/new-releases"  # Replace with the correct URL

# Send a GET request to fetch the page content
response = requests.get(URL)
response.raise_for_status()  # Ensure the request was successful

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Find all the <a> tags inside the specified div container
book_links = []
containers = soup.find_all("div", class_="flexbox-not-mobile is-clearfix")

for container in containers:
    link_tag = container.find("a", class_="col")
    if link_tag:
        # Append the full URL of the book
        book_links.append(f"https://romance.io{link_tag['href']}")

# Output the extracted book links
print("Extracted Book Links:")
for link in book_links:
    print(link)
