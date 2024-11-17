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
    "T": [],
    "G": [],
    "R": [],
    "A": [],
    "M": [],
    "F": [],
    "S": [],
    "SG": [],
    "C": [],
    "CW": [],
    "RC": [],
    "SP": [],
}


def classify_tag(tag, category_code):
    """Classify a tag under the given category code, avoiding duplicates."""
    if tag not in classified_tags[category_code]:
        classified_tags[category_code].append(tag)
        print(f"Tag '{tag}' classified under category '{category_code}'.")
    else:
        print(f"Tag '{tag}' is already classified under category '{category_code}'.")


def write_to_google_sheet_with_headers(service, spreadsheet_id, category_code, tag):
    """
    Writes a new tag and its category to the Google Sheet immediately after entry.

    :param service: The Google Sheets service object.
    :param spreadsheet_id: The ID of the Google Spreadsheet.
    :param category_code: The short code of the category (e.g., "T" for Trope).
    :param tag: The tag entered by the user.
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

        # Prepare data for the new entry
        new_entry = [[tag, category_code]]

        # Append the new entry to the sheet
        body = {
            "values": new_entry
        }

        response = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range="Tag Label!A:B",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body=body
        ).execute()

        print(f"Successfully added: {tag} under category {category_code}")

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
          CW: Content Warnings
          RC: Race, Culture, and Religion
          SP: Sports
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
            "CW": "Content Warnings",
            "RC": "Race, Culture, and Religion",
            "SP": "Sports",
        }
        category = input("Enter the letter corresponding to the category: ").strip().upper()
        if category in category_map:
            classify_tag(tag, category)
            write_to_google_sheet_with_headers(service, SPREADSHEET_ID, category, tag)
        else:
            print("Invalid category. Try again.")

    print("--- Finished ---")


if __name__ == "__main__":
    main()
