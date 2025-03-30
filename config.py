"""
Configuration settings for the Read Later project.
Centralizes configuration values that may need to be updated.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Google Sheets Configuration
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
if not SPREADSHEET_ID:
    raise ValueError("SPREADSHEET_ID environment variable is not set")

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
URL_COLUMN = 'Source' # Column name for the URL - used as primary key

# Database Configuration
DB_PATH = 'read_later.db'
TABLE_NAME = 'articles'

# Airflow Configuration
DAG_SCHEDULE = '0 8 * * *'  # Run daily at 8:00 AM
DAG_START_DATE = '2024-01-01'
DAG_TAGS = ['read_later', 'sync']
DAG_TIMEOUT = 30  # minutes
