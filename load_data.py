"""
Google Sheets Synchronization Script

This script connects to Google Sheets API and downloads the specified spreadsheet.
It requires proper authentication setup with Google Cloud Platform.
"""

import os
import pandas as pd
import duckdb
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
from datetime import datetime
from config import SPREADSHEET_ID, SCOPES, DB_PATH, TABLE_NAME, URL_COLUMN

def get_google_sheets_service():
    """
    Authenticate and create a Google Sheets service.
    Returns the service object.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    return service

def download_spreadsheet(spreadsheet_id, sheet_name=None):
    """
    Download a spreadsheet from Google Sheets.
    
    Args:
        spreadsheet_id (str): The ID of the spreadsheet
        sheet_name (str, optional): Name of the specific sheet to download
    
    Returns:
        pandas.DataFrame: The spreadsheet data as a DataFrame
    """
    service = get_google_sheets_service()
    
    # Get the spreadsheet
    sheet = service.spreadsheets()
    
    # Get all sheets in the spreadsheet
    spreadsheet = sheet.get(spreadsheetId=spreadsheet_id).execute()
    
    # If no sheet name specified, use the first sheet
    if not sheet_name:
        sheet_name = spreadsheet['sheets'][0]['properties']['title']
    
    # Get the data from the specified sheet
    result = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=sheet_name
    ).execute()
    
    # Convert to DataFrame
    values = result.get('values', [])
    if not values:
        print('No data found.')
        return None
    
    # Create DataFrame
    df = pd.DataFrame(values[1:], columns=values[0])
    
    # Add timestamp for when the data was pulled
    df['last_updated'] = datetime.now().isoformat()
    
    return df

def setup_database(df):
    """
    Set up the DuckDB database and create the articles table if it doesn't exist.
    """
    conn = duckdb.connect(DB_PATH)
    
    # Create table if it doesn't exist
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} 
        as SELECT * FROM df
    """)

    # Set primary key on URL
    conn.execute(f"""
        ALTER TABLE {TABLE_NAME} ADD PRIMARY KEY ({URL_COLUMN})
    """)

    conn.close()

    
    # Insert initial data if table is empty
    if conn.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0] == 0:
        conn.execute(f"""
            INSERT INTO {TABLE_NAME} 
            BY NAME (SELECT * FROM df)
        """)
    
    return conn

def upsert_data(conn, df):
    """
    Insert new data into DuckDB, ignoring any records that already exist.
    Uses URL (Source) as the unique identifier.
    
    Args:
        conn: DuckDB connection
        df: pandas DataFrame with the new data
    
    Returns:
        int: Number of new records added
    """
    # Get count before insert
    count_before = conn.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0]
    
    # Perform insert using INSERT OR IGNORE
    conn.execute(f"""
        INSERT OR IGNORE INTO {TABLE_NAME} 
        BY NAME (SELECT * FROM df)
    """)
    
    # Get count after insert
    count_after = conn.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0]
    new_records = count_after - count_before
    
    print(f"Total records in database: {count_after}")
    print(f"New records added in this sync: {new_records}")
    
    return new_records

def main():
    try:
        # Download the spreadsheet
        df = download_spreadsheet(SPREADSHEET_ID)
        
        if df is not None:
            # Set up database connection
            conn = setup_database(df)
            
            # Upsert the data and get count of new records
            new_records = upsert_data(conn, df)
            
            # Close the connection
            conn.close()
            
            print("Successfully synchronized data with DuckDB")
            return new_records
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return 0

if __name__ == '__main__':
    main() 