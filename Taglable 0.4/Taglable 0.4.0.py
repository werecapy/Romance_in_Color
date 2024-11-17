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


def write_to_google_sheet():
    """Write the classified tags to a Google Sheet."""
    values = [["Category", "Tags"]]
    for category, tags in classified_tags.items():
        values.append([category, ", ".join(tags)])

    # Write to Google Sheet
    body = {"values": values}
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range="Tag Label!A1",  # Replace 'Sheet1' with the name of your tab
        valueInputOption="RAW",
        body=body
    ).execute()
    print("Results have been written to the Google Sheet.")


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

    # Prepare data for writing
    tags_to_write = []
    for category, tags in classified_tags.items():
        for tag in tags:
            tags_to_write.append(f"{category}: {tag}")

    # Call the function to write data
    write_to_tag_label_sheet(service, SPREADSHEET_ID, tags_to_write)


def write_to_tag_label_sheet(service, spreadsheet_id, data):
    """
    Writes data to the 'Tag Label' sheet of a Google Spreadsheet.
    Prevents duplicates before writing.

    :param service: The Google Sheets service object.
    :param spreadsheet_id: The ID of the Google Spreadsheet.
    :param data: A list of tags to write.
    """
    try:
        # Read existing data
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range="Tag Label!A:A"  # Assuming tags are in column A
        ).execute()
        existing_values = result.get('values', [])
        existing_tags = set(row[0] for row in existing_values if row)

        # Remove duplicates
        new_tags = [tag for tag in data if tag not in existing_tags]

        if not new_tags:
            print("No new tags to add.")
            return

        # Prepare request body
        body = {
            "values": [[tag] for tag in new_tags]
        }

        # Append new data
        response = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range="Tag Label!A:A",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body=body
        ).execute()

        print("Write successful:", response)
    except Exception as e:
        print(f"Error writing to sheet: {e}")


if __name__ == "__main__":
    main()
