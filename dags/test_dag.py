from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# Define default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 3, 30),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the Python function
def print_hello():
    return "Hello from Airflow!"

# Define the DAG
dag = DAG(
    'test_dag',
    default_args=default_args,
    description='A simple test DAG',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['test'],
)

# Define tasks
task1 = PythonOperator(
    task_id='hello_task',
    python_callable=print_hello,
    dag=dag,
)

task2 = BashOperator(
    task_id='bash_task',
    bash_command='echo "Hello from Bash!"',
    dag=dag,
)

# Set task dependencies
task1 >> task2 