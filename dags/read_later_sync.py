"""
Airflow DAG for Read Later data synchronization.

This DAG runs the load_data.py script on a schedule to sync data from Google Sheets
to the local DuckDB database.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import os
import sys

# Add project root to Python path to import config
DAG_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(DAG_DIR)
sys.path.append(PROJECT_ROOT)

from config import (
    SPREADSHEET_ID,
    SCOPES,
    DB_PATH,
    TABLE_NAME,
    DAG_SCHEDULE,
    DAG_START_DATE,
    DAG_TAGS,
    DAG_TIMEOUT
)

# Define virtual environment path
VENV_PYTHON = os.path.join(PROJECT_ROOT, 'venv', 'bin', 'python')

# Define default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(minutes=DAG_TIMEOUT),
}

# Define the DAG
dag = DAG(
    'read_later_sync',
    default_args=default_args,
    description='Sync Read Later data from Google Sheets to DuckDB',
    schedule_interval=DAG_SCHEDULE,
    start_date=datetime.strptime(DAG_START_DATE, '%Y-%m-%d'),
    catchup=False,
    tags=DAG_TAGS,
)

def run_sync():
    """Run the data synchronization script using the project's virtual environment."""
    # Get the absolute path to the load_data.py script
    script_path = os.path.join(PROJECT_ROOT, 'load_data.py')
    
    # Execute the script using the project's virtual environment
    os.system(f'{VENV_PYTHON} {script_path}')

# Define the task
sync_task = PythonOperator(
    task_id='sync_data',
    python_callable=run_sync,
    dag=dag,
)

# Set task dependencies (in this case, we only have one task)
sync_task 