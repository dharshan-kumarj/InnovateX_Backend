import gspread
import json
from google.oauth2.service_account import Credentials
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

def scan_google_sheets():
    try:
        # Load credentials
        print("Loading credentials...")
        with open('credentials.json', 'r') as f:
            creds_info = json.load(f)
        
        # Set up the credentials and authorize
        print("Setting up credentials...")
        scope = [
            'https://www.googleapis.com/auth/spreadsheets.readonly',
            'https://www.googleapis.com/auth/drive.readonly'
        ]
        
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        
        # Extract spreadsheet ID from URL
        sheet_id = "1I7ddC_ij6L0fnkowLMBjxiZzKF7eICEktYobUXpPCVI"
        print(f"Attempting to open spreadsheet with ID: {sheet_id}")
        
        # Try to open the spreadsheet
        spreadsheet = client.open_by_key(sheet_id)
        print(f"Successfully opened spreadsheet: {spreadsheet.title}")
        
        # Get the specific worksheet by gid (1893068366)
        print("Getting worksheets...")
        worksheets = spreadsheet.worksheets()
        print(f"Found {len(worksheets)} worksheets:")
        
        for ws in worksheets:
            print(f"  - {ws.title} (ID: {ws.id})")
        
        target_worksheet = None
        
        # Try to find worksheet by gid
        for worksheet in worksheets:
            if str(worksheet.id) == "1893068366":
                target_worksheet = worksheet
                break
        
        if not target_worksheet:
            print(f"Worksheet with gid 1893068366 not found. Using first worksheet: {worksheets[0].title}")
            target_worksheet = worksheets[0]
        else:
            print(f"Found target worksheet: {target_worksheet.title}")
        
        # Get all values from the sheet
        print("Getting all values from the sheet...")
        all_values = target_worksheet.get_all_values()
        
        if not all_values:
            print("No data found in the sheet.")
            return
        
        print(f"Found {len(all_values)} rows of data")
        print("Headers:", all_values[0])
        
        # Find columns for team name and domains
        header_row = all_values[0]
        team_name_col = None
        domains_col = None
        
        # Look for team name column (case insensitive)
        for i, header in enumerate(header_row):
            header_lower = header.lower()
            print(f"Column {i}: '{header}' -> '{header_lower}'")
            
            if ('team' in header_lower and 'name' in header_lower) or header_lower == 'team name':
                team_name_col = i
                print(f"Found team name column at index {i}")
            elif 'domain' in header_lower:
                domains_col = i
                print(f"Found domains column at index {i}")
        
        # If exact matches not found, try broader search
        if team_name_col is None:
            for i, header in enumerate(header_row):
                if 'team' in header.lower():
                    team_name_col = i
                    print(f"Using broader match for team column at index {i}: '{header}'")
                    break
        
        if domains_col is None:
            for i, header in enumerate(header_row):
                if any(word in header.lower() for word in ['domain', 'website', 'url', 'site']):
                    domains_col = i
                    print(f"Using broader match for domains column at index {i}: '{header}'")
                    break
        
        if team_name_col is None or domains_col is None:
            print("Could not find team name or domains columns.")
            print("Available headers:", header_row)
            print("Please check the column names in your spreadsheet.")
            return
        
        # Extract team names and domains
        team_data = []
        for row_idx, row in enumerate(all_values[1:], 1):  # Skip header row
            if len(row) > max(team_name_col, domains_col):
                team_name = row[team_name_col].strip() if team_name_col < len(row) else ""
                domains = row[domains_col].strip() if domains_col < len(row) else ""
                
                if team_name and domains:  # Only include rows with both values
                    team_data.append({
                        'team_name': team_name,
                        'domains': domains
                    })
                    print(f"Row {row_idx}: {team_name} -> {domains}")
        
        # Output the results
        print("\n" + "=" * 50)
        print(f"Found {len(team_data)} teams with data:")
        print("=" * 50)
        
        for i, team in enumerate(team_data, 1):
            print(f"{i}. Team Name: {team['team_name']}")
            print(f"   Domains: {team['domains']}")
            print("-" * 30)
        
        return team_data
        
    except Exception as e:
        print(f"Error accessing the sheet: {e}")
        print("Full error traceback:")
        traceback.print_exc()
        print("\nTroubleshooting steps:")
        print("1. Make sure the service account email has been shared with the Google Sheet")
        print("2. Check if the spreadsheet ID is correct")
        print("3. Verify the credentials.json file is valid")
        return None

# Create FastAPI app
app = FastAPI(
    title="Team Domains API",
    description="API to fetch team names and domains from Google Sheets",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # React default
        "http://localhost:5173",    # Vite default
        "http://localhost:8080",    # Vue default
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "*"  # Allow all origins (use with caution in production)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/teams")
async def get_teams():
    """API endpoint to fetch team names and domains"""
    try:
        data = scan_google_sheets()
        
        if data is None:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to fetch data from Google Sheets",
                    "message": "Check server logs for details"
                }
            )
        
        return {
            "success": True,
            "count": len(data),
            "teams": data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": str(e)
            }
        )

@app.get("/")
async def home():
    """Home endpoint with API information"""
    return {
        "message": "Team Domains API",
        "endpoints": {
            "/teams": "GET - Fetch all team names and domains",
            "/": "GET - API information",
            "/docs": "GET - Interactive API documentation",
            "/redoc": "GET - Alternative API documentation"
        },
        "example_response": {
            "success": True,
            "count": 2,
            "teams": [
                {
                    "team_name": "Example Team",
                    "domains": "example.com"
                }
            ]
        }
    }

if __name__ == "__main__":
    # Run the FastAPI app
    print("Starting Team Domains API with FastAPI...")
    print("CORS enabled for frontend development")
    print("API Endpoints:")
    print("  GET /teams - Fetch all team names and domains")
    print("  GET /      - API information")
    print("  GET /docs  - Interactive API documentation (Swagger UI)")
    print("  GET /redoc - Alternative API documentation")
    print("\nStarting server on http://localhost:8000")
    
    uvicorn.run("sheets_scanner:app", host="0.0.0.0", port=8000, reload=True)