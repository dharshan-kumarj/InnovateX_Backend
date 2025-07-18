import json
import gspread
from google.oauth2.service_account import Credentials

def test_credentials():
    try:
        # Load credentials
        print("Loading credentials...")
        with open('credentials.json', 'r') as f:
            creds_info = json.load(f)
        
        print(f"Project ID: {creds_info.get('project_id')}")
        print(f"Client Email: {creds_info.get('client_email')}")
        
        # Test credential creation
        scope = [
            'https://www.googleapis.com/auth/spreadsheets.readonly',
            'https://www.googleapis.com/auth/drive.readonly'
        ]
        
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        print("✓ Credentials loaded successfully")
        
        # Test actual API connection
        print("Testing Google Sheets API connection...")
        client = gspread.authorize(creds)
        print("✓ Google Sheets API connection successful!")
        
        # Test opening the specific sheet
        sheet_id = "1I7ddC_ij6L0fnkowLMBjxiZzKF7eICEktYobUXpPCVI"
        print(f"Testing access to spreadsheet...")
        
        try:
            spreadsheet = client.open_by_key(sheet_id)
            print(f"✓ Successfully accessed spreadsheet: {spreadsheet.title}")
            print("✓ All tests passed! Your setup is working.")
        except Exception as sheet_error:
            print(f"✗ Cannot access spreadsheet: {sheet_error}")
            print("💡 You need to share the Google Sheet with:")
            print(f"   {creds_info.get('client_email')}")
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_credentials()