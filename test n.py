import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Setup Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    '/Users/lizkoempel/Documents/subgenreincolor-c0bb73e9b81b.json', scope)
client = gspread.authorize(creds)

# Open the sheet
spreadsheet = client.open("Romance Books")
worksheet = spreadsheet.worksheet("Book Details")

# Write a test row
worksheet.append_row(['Test Title', 'Test Author', '5.0', '5', '2024-11-16', 'No Image', 'test tag', 'No warnings'])
print("Test data written successfully.")
