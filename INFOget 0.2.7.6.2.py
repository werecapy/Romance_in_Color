def write_to_google_sheets(data, spreadsheet_name, worksheet_name):
    """
    Writes extracted book data to Google Sheets.

    Parameters:
        data (dict): The book information dictionary.
        spreadsheet_name (str): Name of the Google Spreadsheet.
        worksheet_name (str): Name of the worksheet/tab within the spreadsheet.
    """
    try:
        # Google Sheets API setup
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            '/Users/lizkoempel/Documents/subgenreincolor-c0bb73e9b81b.json', scope)
        client = gspread.authorize(creds)

        # Test if the spreadsheet can be accessed
        spreadsheet = client.open("Romance_in_Color")
        worksheet = spreadsheet.worksheet("pages")

        print(f"Successfully opened worksheet: {worksheet_name} in {spreadsheet_name}")

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

    except gspread.exceptions.APIError as api_error:
        print(f"API error occurred: {api_error}")
    except gspread.exceptions.SpreadsheetNotFound as e:
        print(f"Spreadsheet not found: {e}")
    except gspread.exceptions.WorksheetNotFound as e:
        print(f"Worksheet not found: {e}")
    except FileNotFoundError as e:
        print(f"Credential file not found: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
