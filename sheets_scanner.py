import gspread
import json
import os
from google.oauth2.service_account import Credentials
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from datetime import datetime

def scan_google_sheets():
    try:
        # Load credentials from environment variables
        print("Loading credentials from environment variables...")
        
        # Check if running on Render (environment variables) or locally (JSON file)
        if os.getenv('GOOGLE_PROJECT_ID'):
            # Use environment variables (for Render deployment)
            creds_info = {
                "type": os.getenv('GOOGLE_CREDENTIALS_TYPE'),
                "project_id": os.getenv('GOOGLE_PROJECT_ID'),
                "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID'),
                "private_key": os.getenv('GOOGLE_PRIVATE_KEY').replace('\\n', '\n'),
                "client_email": os.getenv('GOOGLE_CLIENT_EMAIL'),
                "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                "auth_uri": os.getenv('GOOGLE_AUTH_URI'),
                "token_uri": os.getenv('GOOGLE_TOKEN_URI'),
                "auth_provider_x509_cert_url": os.getenv('GOOGLE_AUTH_PROVIDER_X509_CERT_URL'),
                "client_x509_cert_url": os.getenv('GOOGLE_CLIENT_X509_CERT_URL'),
                "universe_domain": os.getenv('GOOGLE_UNIVERSE_DOMAIN')
            }
            print("✓ Using environment variables for credentials")
        else:
            # Use local JSON file (for local development)
            with open('credentials.json', 'r') as f:
                creds_info = json.load(f)
            print("✓ Using local credentials.json file")
        
        # Set up the credentials and authorize
        print("Setting up credentials...")
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
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
        
        # Find columns for team name, domains, and team leader
        header_row = all_values[0]
        team_name_col = None
        domains_col = None
        team_leader_col = None
        
        # Look for team name, domains, and team leader columns (case insensitive)
        for i, header in enumerate(header_row):
            header_lower = header.lower()
            print(f"Column {i}: '{header}' -> '{header_lower}'")
            
            if ('team' in header_lower and 'name' in header_lower) or header_lower == 'team name':
                team_name_col = i
                print(f"Found team name column at index {i}")
            elif 'domain' in header_lower:
                domains_col = i
                print(f"Found domains column at index {i}")
            elif ('team' in header_lower and 'leader' in header_lower and 'name' in header_lower and 'reg' in header_lower) or \
                 ('leader' in header_lower and 'name' in header_lower and 'reg' in header_lower) or \
                 ('leader' in header_lower and ('name' in header_lower or 'reg' in header_lower) and 'number' not in header_lower and 'whatsapp' not in header_lower):
                team_leader_col = i
                print(f"Found team leader (name & reg) column at index {i}")
        
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
        
        if team_leader_col is None:
            for i, header in enumerate(header_row):
                header_lower = header.lower()
                # Look for team leader with name/reg but exclude number/whatsapp columns
                if ('leader' in header_lower and 
                    ('name' in header_lower or 'reg' in header_lower) and 
                    'number' not in header_lower and 
                    'whatsapp' not in header_lower and
                    'phone' not in header_lower):
                    team_leader_col = i
                    print(f"Using broader match for team leader (name & reg) column at index {i}: '{header}'")
                    break
        
        if team_name_col is None or domains_col is None:
            print("Could not find team name or domains columns.")
            print("Available headers:", header_row)
            print("Please check the column names in your spreadsheet.")
            return
        
        # Extract team names, domains, and team leaders
        team_data = []
        for row_idx, row in enumerate(all_values[1:], 1):  # Skip header row
            if len(row) > max(team_name_col, domains_col, team_leader_col or 0):
                team_name = row[team_name_col].strip() if team_name_col < len(row) else ""
                domains = row[domains_col].strip() if domains_col < len(row) else ""
                team_leader = row[team_leader_col].strip() if team_leader_col is not None and team_leader_col < len(row) else ""
                
                if team_name and domains:  # Only include rows with both values
                    team_entry = {
                        'team_name': team_name,
                        'domains': domains
                    }
                    
                    # Add team leader if available
                    if team_leader:
                        team_entry['team_leader'] = team_leader
                    
                    team_data.append(team_entry)
                    print(f"Row {row_idx}: {team_name} -> {domains}" + (f" (Leader: {team_leader})" if team_leader else ""))
        
        # Output the results
        print("\n" + "=" * 50)
        print(f"Found {len(team_data)} teams with data:")
        print("=" * 50)
        
        for i, team in enumerate(team_data, 1):
            print(f"{i}. Team Name: {team['team_name']}")
            print(f"   Domains: {team['domains']}")
            if 'team_leader' in team:
                print(f"   Team Leader: {team['team_leader']}")
            print("-" * 30)
        
        return team_data
        
    except Exception as e:
        print(f"Error accessing the sheet: {e}")
        print("Full error traceback:")
        traceback.print_exc()
        print("\nTroubleshooting steps:")
        print("1. Make sure the service account email has been shared with the Google Sheet")
        print("2. Check if the spreadsheet ID is correct")
        print("3. Verify the credentials are valid")
        return None

# Pydantic model for single attendance record
class AttendanceRecord(BaseModel):
    regno: str
    name: str
    day: str
    event_type: str
    category: str = None  # Make category optional

# Pydantic model for mass attendance request
class MassAttendanceRequest(BaseModel):
    attendance_records: list[AttendanceRecord]

def save_attendance_to_sheets(regno: str, name: str, day: str, event_type: str, category: str = None):
    try:
        # Validation
        if not regno or not name or not day or not event_type:
            return {"error": "Registration number, name, day, and event_type are required"}
        
        # Event type validation
        if event_type.lower() not in ["bootcamp", "hackathon"]:
            return {"error": "Invalid event_type. Use 'bootcamp' or 'hackathon'"}
        
        # Day validation based on event type
        if event_type.lower() == "bootcamp":
            if day not in ["1", "2", "3", "4", "5"]:
                return {"error": "Invalid day for bootcamp. Use '1', '2', '3', '4', or '5'"}
            # Category is required for bootcamp
            if not category:
                return {"error": "Category is required for bootcamp events"}
        elif event_type.lower() == "hackathon":
            if day not in ["1", "2"]:
                return {"error": "Invalid day for hackathon. Use '1' or '2'"}
            # Category is not needed for hackathon, set default
            category = "General"
        
        # Load credentials (same as scan_google_sheets function)
        print("Loading credentials for attendance saving...")
        
        if os.getenv('GOOGLE_PROJECT_ID'):
            creds_info = {
                "type": os.getenv('GOOGLE_CREDENTIALS_TYPE'),
                "project_id": os.getenv('GOOGLE_PROJECT_ID'),
                "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID'),
                "private_key": os.getenv('GOOGLE_PRIVATE_KEY').replace('\\n', '\n'),
                "client_email": os.getenv('GOOGLE_CLIENT_EMAIL'),
                "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                "auth_uri": os.getenv('GOOGLE_AUTH_URI'),
                "token_uri": os.getenv('GOOGLE_TOKEN_URI'),
                "auth_provider_x509_cert_url": os.getenv('GOOGLE_AUTH_PROVIDER_X509_CERT_URL'),
                "client_x509_cert_url": os.getenv('GOOGLE_CLIENT_X509_CERT_URL'),
                "universe_domain": os.getenv('GOOGLE_UNIVERSE_DOMAIN')
            }
        else:
            with open('credentials.json', 'r') as f:
                creds_info = json.load(f)
        
        # Set up credentials with write permissions
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        
        # Attendance spreadsheet ID (from the provided link)
        attendance_sheet_id = "1Nw0GzQuxKZYefPGPRvcQZk4RlkRnZLsIwPc6RD7SPBI"
        
        # Open the attendance spreadsheet
        spreadsheet = client.open_by_key(attendance_sheet_id)
        print(f"Successfully opened attendance spreadsheet: {spreadsheet.title}")
        
        # Determine which worksheet to use based on event_type and category
        worksheet_name = None
        
        if event_type.lower() == "bootcamp":
            if category.lower() in ["ai/ml", "ai", "ml", "artificial intelligence", "machine learning"]:
                worksheet_name = "AI/ML Bootcamp"
            elif category.lower() in ["cyber", "cybersecurity", "security"]:
                worksheet_name = "Cyber Bootcamp"
            elif category.lower() in ["full stack", "fullstack", "web development", "web dev"]:
                worksheet_name = "Full Stack Development"
            else:
                return {"error": f"Invalid bootcamp category: {category}. Use 'AI/ML', 'Cyber', or 'Full Stack'"}
        
        elif event_type.lower() == "hackathon":
            if day == "1":
                worksheet_name = "Hackathon Day 1"
            elif day == "2":
                worksheet_name = "Hackathon Day 2"
            else:
                return {"error": f"Invalid hackathon day: {day}. Only days 1-2 are supported for hackathon."}
        
        else:
            return {"error": f"Invalid event type: {event_type}. Use 'bootcamp' or 'hackathon'"}
        
        # Try to find the worksheet
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
            print(f"Found existing worksheet: {worksheet_name}")
        except gspread.WorksheetNotFound:
            # If worksheet doesn't exist, try to create it
            try:
                print(f"Worksheet '{worksheet_name}' not found. Attempting to create it...")
                worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=10)
                # Add headers with name field
                headers = ["Registration Number", "Name", "Day", "Timestamp", "Event Type", "Category"]
                worksheet.append_row(headers)
                print(f"Successfully created worksheet: {worksheet_name}")
            except gspread.exceptions.APIError as api_error:
                if "403" in str(api_error):
                    return {
                        "error": "Permission denied",
                        "message": f"The service account doesn't have permission to create worksheet '{worksheet_name}'. Please ensure the service account has editor permissions on the spreadsheet, or manually create the worksheet with headers: Registration Number, Name, Day, Timestamp, Event Type, Category"
                    }
                else:
                    return {"error": f"API error creating worksheet: {str(api_error)}"}
            except Exception as create_error:
                return {"error": f"Error creating worksheet: {str(create_error)}"}
        
        # Get current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Prepare the row data with name field
        row_data = [regno, name, day, timestamp, event_type, category]
        
        # Check if this regno and day combination already exists
        all_records = worksheet.get_all_records()
        duplicate_found = False
        
        for record in all_records:
            if (str(record.get('Registration Number', '')).strip() == regno.strip() and 
                str(record.get('Day', '')).strip() == day.strip()):
                duplicate_found = True
                break
        
        if duplicate_found:
            return {
                "error": "Duplicate entry",
                "message": f"Attendance for regno {regno} on day {day} already recorded"
            }
        
        # Append the new row
        try:
            worksheet.append_row(row_data)
            print(f"Successfully added attendance for {regno} - {name}")
            
            return {
                "success": True,
                "message": f"Attendance recorded successfully for {regno} - {name}",
                "data": {
                    "regno": regno,
                    "name": name,
                    "day": day,
                    "event_type": event_type,
                    "category": category,
                    "timestamp": timestamp,
                    "worksheet": worksheet_name
                }
            }
        except gspread.exceptions.APIError as api_error:
            if "403" in str(api_error):
                return {
                    "error": "Permission denied",
                    "message": "The service account doesn't have permission to write to this worksheet. Please ensure the service account has editor permissions on the spreadsheet."
                }
            else:
                return {"error": f"API error saving attendance: {str(api_error)}"}
        
    except Exception as e:
        print(f"Error saving attendance: {str(e)}")
        return {"error": f"Internal server error: {str(e)}"}

def save_mass_attendance_to_sheets(attendance_records: list):
    """
    Save multiple attendance records to Google Sheets
    """
    try:
        results = []
        success_count = 0
        error_count = 0
        
        for record in attendance_records:
            result = save_attendance_to_sheets(
                regno=record.regno,
                name=record.name, 
                day=record.day,
                event_type=record.event_type,
                category=record.category
            )
            
            if "success" in result:
                success_count += 1
            else:
                error_count += 1
            
            results.append({
                "regno": record.regno,
                "name": record.name,
                "result": result
            })
        
        return {
            "success": True,
            "message": f"Mass attendance processing completed. Success: {success_count}, Errors: {error_count}",
            "summary": {
                "total_records": len(attendance_records),
                "successful": success_count,
                "failed": error_count
            },
            "detailed_results": results
        }
        
    except Exception as e:
        return {"error": f"Error processing mass attendance: {str(e)}"}
    try:
        # Validation
        if not regno or not day or not event_type:
            return {"error": "Registration number, day, and event_type are required"}
        
        # Event type validation
        if event_type.lower() not in ["bootcamp", "hackathon"]:
            return {"error": "Invalid event_type. Use 'bootcamp' or 'hackathon'"}
        
        # Day validation based on event type
        if event_type.lower() == "bootcamp":
            if day not in ["1", "2", "3", "4", "5"]:
                return {"error": "Invalid day for bootcamp. Use '1', '2', '3', '4', or '5'"}
            # Category is required for bootcamp
            if not category:
                return {"error": "Category is required for bootcamp events"}
        elif event_type.lower() == "hackathon":
            if day not in ["1", "2"]:
                return {"error": "Invalid day for hackathon. Use '1' or '2'"}
            # Category is not needed for hackathon, set default
            category = "General"
        
        # Load credentials (same as scan_google_sheets function)
        print("Loading credentials for attendance saving...")
        
        if os.getenv('GOOGLE_PROJECT_ID'):
            creds_info = {
                "type": os.getenv('GOOGLE_CREDENTIALS_TYPE'),
                "project_id": os.getenv('GOOGLE_PROJECT_ID'),
                "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID'),
                "private_key": os.getenv('GOOGLE_PRIVATE_KEY').replace('\\n', '\n'),
                "client_email": os.getenv('GOOGLE_CLIENT_EMAIL'),
                "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                "auth_uri": os.getenv('GOOGLE_AUTH_URI'),
                "token_uri": os.getenv('GOOGLE_TOKEN_URI'),
                "auth_provider_x509_cert_url": os.getenv('GOOGLE_AUTH_PROVIDER_X509_CERT_URL'),
                "client_x509_cert_url": os.getenv('GOOGLE_CLIENT_X509_CERT_URL'),
                "universe_domain": os.getenv('GOOGLE_UNIVERSE_DOMAIN')
            }
        else:
            with open('credentials.json', 'r') as f:
                creds_info = json.load(f)
        
        # Set up credentials with write permissions
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        
        # Attendance spreadsheet ID (from the provided link)
        attendance_sheet_id = "1Nw0GzQuxKZYefPGPRvcQZk4RlkRnZLsIwPc6RD7SPBI"
        
        # Open the attendance spreadsheet
        spreadsheet = client.open_by_key(attendance_sheet_id)
        print(f"Successfully opened attendance spreadsheet: {spreadsheet.title}")
        
        # Determine which worksheet to use based on event_type and category
        worksheet_name = None
        
        if event_type.lower() == "bootcamp":
            if category.lower() in ["ai/ml", "ai", "ml", "artificial intelligence", "machine learning"]:
                worksheet_name = "AI/ML Bootcamp"
            elif category.lower() in ["cyber", "cybersecurity", "security"]:
                worksheet_name = "Cyber Bootcamp"
            elif category.lower() in ["full stack", "fullstack", "web development", "web dev"]:
                worksheet_name = "Full Stack Development"
            else:
                return {"error": f"Invalid bootcamp category: {category}. Use 'AI/ML', 'Cyber', or 'Full Stack'"}
        
        elif event_type.lower() == "hackathon":
            if day == "1":
                worksheet_name = "Hackathon Day 1"
            elif day == "2":
                worksheet_name = "Hackathon Day 2"
            else:
                return {"error": f"Invalid hackathon day: {day}. Only days 1-2 are supported for hackathon."}
        
        else:
            return {"error": f"Invalid event type: {event_type}. Use 'bootcamp' or 'hackathon'"}
        
        # Try to find the worksheet
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
            print(f"Found existing worksheet: {worksheet_name}")
        except gspread.WorksheetNotFound:
            # If worksheet doesn't exist, try to create it
            try:
                print(f"Worksheet '{worksheet_name}' not found. Attempting to create it...")
                worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=10)
                # Add headers
                headers = ["Registration Number", "Day", "Timestamp", "Event Type", "Category"]
                worksheet.append_row(headers)
                print(f"Successfully created worksheet: {worksheet_name}")
            except gspread.exceptions.APIError as api_error:
                if "403" in str(api_error):
                    return {
                        "error": "Permission denied",
                        "message": f"The service account doesn't have permission to create worksheet '{worksheet_name}'. Please ensure the service account has editor permissions on the spreadsheet, or manually create the worksheet with headers: Registration Number, Day, Timestamp, Event Type, Category"
                    }
                else:
                    return {"error": f"API error creating worksheet: {str(api_error)}"}
            except Exception as create_error:
                return {"error": f"Error creating worksheet: {str(create_error)}"}
        
        # Get current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Prepare the row data
        row_data = [regno, day, timestamp, event_type, category]
        
        # Check if this regno and day combination already exists
        all_records = worksheet.get_all_records()
        duplicate_found = False
        
        for record in all_records:
            if (str(record.get('Registration Number', '')).strip() == regno.strip() and 
                str(record.get('Day', '')).strip() == day.strip()):
                duplicate_found = True
                break
        
        if duplicate_found:
            return {
                "error": "Duplicate entry",
                "message": f"Attendance for regno {regno} on day {day} already recorded"
            }
        
        # Append the new row
        try:
            worksheet.append_row(row_data)
            print(f"Successfully added attendance for {regno}")
            
            return {
                "success": True,
                "message": f"Attendance recorded successfully for {regno}",
                "data": {
                    "regno": regno,
                    "day": day,
                    "event_type": event_type,
                    "category": category,
                    "timestamp": timestamp,
                    "worksheet": worksheet_name
                }
            }
        except gspread.exceptions.APIError as api_error:
            if "403" in str(api_error):
                return {
                    "error": "Permission denied",
                    "message": "The service account doesn't have permission to write to this worksheet. Please ensure the service account has editor permissions on the spreadsheet."
                }
            else:
                return {"error": f"API error saving attendance: {str(api_error)}"}
        
    except Exception as e:
        print(f"Error saving attendance: {str(e)}")
        return {"error": f"Internal server error: {str(e)}"}

def get_teams_by_category(category: str):
    """
    Retrieve team names and team leaders from specific Google Sheets based on category
    """
    try:
        # Load credentials (same as other functions)
        print(f"Loading credentials for category: {category}")
        
        if os.getenv('GOOGLE_PROJECT_ID'):
            creds_info = {
                "type": os.getenv('GOOGLE_CREDENTIALS_TYPE'),
                "project_id": os.getenv('GOOGLE_PROJECT_ID'),
                "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID'),
                "private_key": os.getenv('GOOGLE_PRIVATE_KEY').replace('\\n', '\n'),
                "client_email": os.getenv('GOOGLE_CLIENT_EMAIL'),
                "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                "auth_uri": os.getenv('GOOGLE_AUTH_URI'),
                "token_uri": os.getenv('GOOGLE_TOKEN_URI'),
                "auth_provider_x509_cert_url": os.getenv('GOOGLE_AUTH_PROVIDER_X509_CERT_URL'),
                "client_x509_cert_url": os.getenv('GOOGLE_CLIENT_X509_CERT_URL'),
                "universe_domain": os.getenv('GOOGLE_UNIVERSE_DOMAIN')
            }
        else:
            with open('credentials.json', 'r') as f:
                creds_info = json.load(f)
        
        # Set up credentials
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        
        # Same spreadsheet ID as the original function
        sheet_id = "1I7ddC_ij6L0fnkowLMBjxiZzKF7eICEktYobUXpPCVI"
        spreadsheet = client.open_by_key(sheet_id)
        
        # Determine which worksheet to use based on category
        target_gid = None
        category_lower = category.lower()
        
        if category_lower in ["ai/ml", "ai", "ml", "aiml"]:
            target_gid = "1880278751"  # AI/ML batch sheet
            print("Using AI/ML batch sheet")
        elif category_lower in ["cyber", "cybersecurity", "security"]:
            target_gid = "1671574899"  # Cyber batch sheet
            print("Using Cyber batch sheet")
        elif category_lower in ["full stack", "fullstack", "full-stack"]:
            # For full stack, we'll return data from both AI/ML and Cyber sheets
            print("Full stack requested - will fetch from both AI/ML and Cyber sheets")
            aiml_data = get_teams_by_category("ai/ml")
            cyber_data = get_teams_by_category("cyber")
            
            if aiml_data and cyber_data and "teams" in aiml_data and "teams" in cyber_data:
                combined_teams = aiml_data["teams"] + cyber_data["teams"]
                return {
                    "success": True,
                    "category": "Full Stack",
                    "count": len(combined_teams),
                    "teams": combined_teams,
                    "sources": ["AI/ML", "Cyber"]
                }
            else:
                return {"error": "Failed to fetch data from AI/ML or Cyber sheets"}
        else:
            return {"error": f"Invalid category: {category}. Use 'AI/ML', 'Cyber', or 'Full Stack'"}
        
        # Get worksheets and find the target one
        worksheets = spreadsheet.worksheets()
        target_worksheet = None
        
        for worksheet in worksheets:
            if str(worksheet.id) == target_gid:
                target_worksheet = worksheet
                break
        
        if not target_worksheet:
            return {"error": f"Worksheet with gid {target_gid} not found for category {category}"}
        
        print(f"Found target worksheet: {target_worksheet.title}")
        
        # Get all values from the sheet
        all_values = target_worksheet.get_all_values()
        
        if not all_values:
            return {"error": "No data found in the sheet"}
        
        # Find columns for all required fields
        header_row = all_values[0]
        team_name_col = None
        team_leader_col = None
        team_member1_col = None
        team_member2_col = None
        reg_leader_col = None
        reg_member1_col = None
        reg_member2_col = None
        
        print(f"Headers: {header_row}")
        
        # Look for all columns with detailed matching
        for i, header in enumerate(header_row):
            header_lower = header.lower().strip()
            print(f"Column {i}: '{header}' -> '{header_lower}'")
            
            # Team Name
            if ('team' in header_lower and 'name' in header_lower) or header_lower == 'team name':
                team_name_col = i
                print(f"Found team name column at index {i}: '{header}'")
            
            # Team Leader
            elif ('team' in header_lower and 'leader' in header_lower) or 'leader' in header_lower:
                if 'reg' not in header_lower and 'number' not in header_lower:
                    team_leader_col = i
                    print(f"Found team leader column at index {i}: '{header}'")
            
            # Team Member 1
            elif ('team' in header_lower and 'member' in header_lower and '1' in header_lower) or \
                 ('member' in header_lower and '1' in header_lower):
                if 'reg' not in header_lower and 'number' not in header_lower:
                    team_member1_col = i
                    print(f"Found team member 1 column at index {i}: '{header}'")
            
            # Team Member 2
            elif ('team' in header_lower and 'member' in header_lower and '2' in header_lower) or \
                 ('member' in header_lower and '2' in header_lower):
                if 'reg' not in header_lower and 'number' not in header_lower:
                    team_member2_col = i
                    print(f"Found team member 2 column at index {i}: '{header}'")
            
            # Registration Numbers - Updated mapping
            elif 'reg' in header_lower and ('number' in header_lower or 'no' in header_lower):
                if 'leader' in header_lower or ('1' in header_lower and 'member' not in header_lower):
                    reg_leader_col = i
                    print(f"Found registration number for leader (Reg Number1) column at index {i}: '{header}'")
                elif '2' in header_lower:
                    reg_member1_col = i  # Reg Number2 goes to reg_member1
                    print(f"Found registration number for member 1 (Reg Number2) column at index {i}: '{header}'")
                elif '3' in header_lower:
                    reg_member2_col = i  # Reg Number3 goes to reg_member2
                    print(f"Found registration number for member 2 (Reg Number3) column at index {i}: '{header}'")
        
        # Broader search if exact matches not found
        if team_name_col is None:
            for i, header in enumerate(header_row):
                if 'team' in header.lower():
                    team_name_col = i
                    print(f"Using broader match for team column at index {i}: '{header}'")
                    break
        
        if team_leader_col is None:
            for i, header in enumerate(header_row):
                if 'leader' in header.lower() and 'reg' not in header.lower():
                    team_leader_col = i
                    print(f"Using broader match for team leader column at index {i}: '{header}'")
                    break
        
        # Look for member columns if not found
        if team_member1_col is None:
            for i, header in enumerate(header_row):
                header_lower = header.lower()
                if 'member' in header_lower and ('1' in header_lower or 'one' in header_lower) and 'reg' not in header_lower:
                    team_member1_col = i
                    print(f"Using broader match for team member 1 column at index {i}: '{header}'")
                    break
        
        if team_member2_col is None:
            for i, header in enumerate(header_row):
                header_lower = header.lower()
                if 'member' in header_lower and ('2' in header_lower or 'two' in header_lower) and 'reg' not in header_lower:
                    team_member2_col = i
                    print(f"Using broader match for team member 2 column at index {i}: '{header}'")
                    break
        
        # Look for registration number columns if not found - Updated logic
        if reg_leader_col is None:
            for i, header in enumerate(header_row):
                header_lower = header.lower()
                if ('reg' in header_lower or 'registration' in header_lower) and \
                   (('1' in header_lower and 'member' not in header_lower) or 'leader' in header_lower):
                    reg_leader_col = i
                    print(f"Using broader match for reg leader (Reg Number1) column at index {i}: '{header}'")
                    break
        
        if reg_member1_col is None:
            for i, header in enumerate(header_row):
                header_lower = header.lower()
                if ('reg' in header_lower or 'registration' in header_lower) and '2' in header_lower:
                    reg_member1_col = i
                    print(f"Using broader match for reg member 1 (Reg Number2) column at index {i}: '{header}'")
                    break
        
        if reg_member2_col is None:
            for i, header in enumerate(header_row):
                header_lower = header.lower()
                if ('reg' in header_lower or 'registration' in header_lower) and '3' in header_lower:
                    reg_member2_col = i
                    print(f"Using broader match for reg member 2 (Reg Number3) column at index {i}: '{header}'")
                    break
        
        if team_name_col is None:
            return {"error": "Could not find team name column"}
        
        # Extract team data with all available information
        teams_data = []
        max_col = max(filter(None, [team_name_col, team_leader_col, team_member1_col, team_member2_col, 
                                   reg_leader_col, reg_member1_col, reg_member2_col]))
        
        for row_idx, row in enumerate(all_values[1:], 1):  # Skip header row
            if len(row) > max_col:
                team_name = row[team_name_col].strip() if team_name_col < len(row) else ""
                
                if team_name:  # Only include rows with team name
                    team_entry = {
                        'team_name': team_name,
                        'team_leader': row[team_leader_col].strip() if team_leader_col is not None and team_leader_col < len(row) else "Not specified",
                        'team_member1': row[team_member1_col].strip() if team_member1_col is not None and team_member1_col < len(row) else "Not specified",
                        'team_member2': row[team_member2_col].strip() if team_member2_col is not None and team_member2_col < len(row) else "Not specified",
                        'reg_leader': row[reg_leader_col].strip() if reg_leader_col is not None and reg_leader_col < len(row) else "Not specified",
                        'reg_member1': row[reg_member1_col].strip() if reg_member1_col is not None and reg_member1_col < len(row) else "Not specified",
                        'reg_member2': row[reg_member2_col].strip() if reg_member2_col is not None and reg_member2_col < len(row) else "Not specified"
                    }
                    teams_data.append(team_entry)
                    print(f"Row {row_idx}: {team_name} -> Leader: {team_entry['team_leader']} ({team_entry['reg_leader']}) | Member1: {team_entry['team_member1']} ({team_entry['reg_member1']}) | Member2: {team_entry['team_member2']} ({team_entry['reg_member2']})")
        
        return {
            "success": True,
            "category": category,
            "count": len(teams_data),
            "teams": teams_data
        }
        
    except Exception as e:
        print(f"Error fetching teams by category: {str(e)}")
        traceback.print_exc()
        return {"error": f"Internal server error: {str(e)}"}

# Create FastAPI app
app = FastAPI(
    title="Team Domains API",
    description="API to fetch team names and domains from Google Sheets",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

@app.post("/attendance")
async def save_attendance(request: MassAttendanceRequest):
    """
    API endpoint to save mass attendance data to Google Sheets
    Accepts an array of attendance records
    """
    try:
        if not request.attendance_records:
            raise HTTPException(status_code=400, detail={"error": "No attendance records provided"})
        
        result = save_mass_attendance_to_sheets(request.attendance_records)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "Internal server error", "message": str(e)})

@app.get("/teams-by-category/{category}")
async def get_teams_by_category_endpoint(category: str):
    """
    API endpoint to fetch team names and team leaders by category
    Categories: AI/ML, Cyber, Full Stack
    """
    try:
        result = get_teams_by_category(category)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "Internal server error", "message": str(e)})

@app.get("/")
async def home():
    """Home endpoint with API information"""
    return {
        "message": "Team Domains API",
        "endpoints": {
            "/teams": "GET - Fetch all team names and domains",
            "/teams-by-category/{category}": "GET - Fetch team names and team leaders by category (AI/ML, Cyber, Full Stack)",
            "/attendance": "POST - Save attendance data to Google Sheets",
            "/": "GET - API information",
            "/docs": "GET - Interactive API documentation",
            "/redoc": "GET - Alternative API documentation"
        },
        "category_examples": {
            "AI/ML": "/teams-by-category/AI/ML or /teams-by-category/AIML",
            "Cyber": "/teams-by-category/Cyber or /teams-by-category/cybersecurity", 
            "Full Stack": "/teams-by-category/Full Stack or /teams-by-category/fullstack"
        },
        "attendance_usage": {
            "method": "POST",
            "endpoint": "/attendance",
            "body": {
                "attendance_records": [
                    {
                        "regno": "Registration number (string)",
                        "name": "Student name (string)",
                        "day": "Day number (1-5 for bootcamp, 1-2 for hackathon)",
                        "event_type": "bootcamp or hackathon",
                        "category": "AI/ML, Cyber, Full Stack (for bootcamp) or any value (for hackathon)"
                    }
                ]
            },
            "examples": {
                "mass_bootcamp_attendance": {
                    "attendance_records": [
                        {
                            "regno": "21ITR001",
                            "name": "John Doe",
                            "day": "1",
                            "event_type": "bootcamp",
                            "category": "AI/ML"
                        },
                        {
                            "regno": "21ITR002", 
                            "name": "Jane Smith",
                            "day": "1",
                            "event_type": "bootcamp",
                            "category": "AI/ML"
                        }
                    ]
                },
                "mass_hackathon_attendance": {
                    "attendance_records": [
                        {
                            "regno": "21ITR001",
                            "name": "John Doe", 
                            "day": "1",
                            "event_type": "hackathon",
                            "category": "Innovation"
                        }
                    ]
                }
            }
        }
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print("Starting Team Domains API with FastAPI...")
    print("CORS enabled for frontend development")
    print(f"Starting server on port {port}")
    
    uvicorn.run("sheets_scanner:app", host="0.0.0.0", port=port, reload=False)