from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# Google Sheets setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = '/Users/lizkoempel/Documents/subgenreincolor-c0bb73e9b81b.json'  # Replace with the path to your credentials JSON file
SPREADSHEET_ID = '1rUaqs21KDwiYbG-6wISvdjFmpmt9Lzu7DuntQ8ZMe-E'  # Replace with your Google Sheet ID

credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()

# Initialize storage for unique tags
classified_tags = {
    "Trope": [],
    "Geographical Setting": [],
    "Relationship Type": [],
    "Act": [],
    "M Personality": [],
    "F Personality": [],
    "Story": [],
    "Subgenre": [],
    "Creatures": [],
}


def classify_tag(tag, category):
    """Classify a tag under the given category, avoiding duplicates."""
    if tag not in classified_tags[category]:
        classified_tags[category].append(tag)
        print(f"Tag '{tag}' classified as '{category}'.")
    else:
        print(f"Tag '{tag}' is already classified as '{category}'.")


def write_to_google_sheet_with_headers(service, spreadsheet_id, data):
    """
    Writes tags and their categories to the 'Tag Label' sheet of a Google Spreadsheet.
    Adds headers if not already present.

    :param service: The Google Sheets service object.
    :param spreadsheet_id: The ID of the Google Spreadsheet.
    :param data: A list of tuples (category, tag) to write.
    """
    try:
        # Read existing data to check for headers and prevent duplication
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range="Tag Label!A:B"  # Check both columns for existing entries
        ).execute()
        existing_values = result.get('values', [])

        # If the sheet is empty, add headers
        if not existing_values:
            headers = [["Tag", "Category"]]
            body = {"values": headers}
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range="Tag Label!A1",
                valueInputOption="RAW",
                body=body
            ).execute()
            print("Headers added to the sheet.")

        # Extract existing tags and categories to prevent duplication
        existing_entries = set(tuple(row) for row in existing_values[1:])  # Skip the header
        new_entries = [(tag, category) for category, tag in data if (tag, category) not in existing_entries]

        if not new_entries:
            print("No new data to write.")
            return

        # Prepare data to append
        body = {
            "values": [[tag, category] for category, tag in new_entries]
        }

        # Append new data to the sheet
        response = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range="Tag Label!A:B",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body=body
        ).execute()

        print(f"Successfully added {len(new_entries)} entries to the sheet.")

    except Exception as e:
        print(f"Error writing to sheet: {e}")


def main():
    print("--- Tag Classification ---")
    while True:
        tag = input("Enter a tag (or type 'done' to finish): ").strip()
        if tag.lower() == 'done':
            break
        print("""
        Categories:
          T: Trope
          G: Geographical Setting
          R: Relationship Type
          A: Act
          M: M Personality
          F: F Personality
          S: Story
          SG: Subgenre
          C: Creatures
        """)
        category_map = {
            "T": "Trope",
            "G": "Geographical Setting",
            "R": "Relationship Type",
            "A": "Act",
            "M": "M Personality",
            "F": "F Personality",
            "S": "Story",
            "SG": "Subgenre",
            "C": "Creatures",
        }
        category = input("Enter the letter corresponding to the category: ").strip().upper()
        if category in category_map:
            classify_tag(tag, category_map[category])
        else:
            print("Invalid category. Try again.")

    print("--- Writing to Google Sheets ---")

    # Prepare data as (category, tag) tuples for writing
    data_to_write = []
    for category, tags in classified_tags.items():
        for tag in tags:
            data_to_write.append((category, tag))

    # Write to Google Sheets with headers
    write_to_google_sheet_with_headers(service, SPREADSHEET_ID, data_to_write)


if __name__ == "__main__":
    main()
