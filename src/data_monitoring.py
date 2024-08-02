import os
import time
import random
import logging
import datetime

import psycopg
from prefect import flow, task
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metrics import (
    ColumnDriftMetric,
    DatasetDriftMetric,
    DatasetMissingValuesMetric,
)

from pipelines.load_data import load_and_preprocess_data
from pipelines.model_registry import ModelRegistry
from pipelines.split_datasets import split_datasets

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s"
)

SEND_TIMEOUT = 10
rand = random.Random()

# Define the environment variables as variables
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_NAME = os.getenv('DB_NAME', 'metrics_db')
METRIC_TABLE = os.getenv('METRIC_TABLE', 'metrics_table')

create_table_statement = f"""
drop table if exists {METRIC_TABLE};
create table {METRIC_TABLE}(
	timestamp timestamp,
	prediction_drift float,
	num_drifted_columns integer,
	share_missing_values float
)
"""

uri = os.getenv("MLFLOW_URI")
experiment_name = "random-forest"

model_registry = ModelRegistry(tracking_uri=uri, experiment_name=experiment_name)


data = load_and_preprocess_data()
val_data = split_datasets(data)['X_test']
train_data = split_datasets(data)['X_train']

begin = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
num_features = val_data.select_dtypes(include=['object', 'bool']).columns.tolist()
cat_features = val_data.select_dtypes(include=['float64', 'int64']).columns.tolist()
column_mapping = ColumnMapping(
    prediction='prediction',
    numerical_features=num_features,
    categorical_features=cat_features,
    target=None,
)

report = Report(
    metrics=[
        ColumnDriftMetric(column_name='prediction'),
        DatasetDriftMetric(),
        DatasetMissingValuesMetric(),
    ]
)


@task
def prep_db():
    """
    generate a database and table for the dummy metrics
    """
    connection = f"host={DB_HOST} port={DB_PORT} user={DB_USER} password={DB_PASSWORD}"
    var = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
    with psycopg.connect(connection, autocommit=True) as conn:
        res = conn.execute(f"SELECT 1 FROM pg_database WHERE datname='{DB_NAME}'")
        if len(res.fetchall()) == 0:
            conn.execute(f"create database {DB_NAME};")
        with psycopg.connect(var) as conn:
            conn.execute(create_table_statement)


@task
def calculate_metrics_postgresql(curr, i):
    """
    Calculate metrics for PostgreSQL database.

    This function calculates metrics for a PostgreSQL database by performing the following steps:
    1. Copies the validation and training data.
    2. Retrieves the model version from the model registry.
    3. Makes predictions on the validation and training data using the model.
    4. Runs a report to calculate metrics based on the reference and current data.
    5. Extracts the required metrics from the report.
    6. Inserts the metrics into the metric table in the PostgreSQL database.

    Parameters:
    - curr: The cursor object for executing SQL queries.
    - i: An integer representing the index.

    Returns:
    None
    """
    val_data_temp = val_data.copy()
    train_data_temp = train_data.copy()
    model = model_registry.get_model_version("random-forest")
    val_data_temp['prediction'] = model.predict(val_data_temp)
    train_data_temp['prediction'] = model.predict(train_data_temp)

    report.run(
        reference_data=train_data_temp,
        current_data=val_data_temp,
        column_mapping=column_mapping,
    )

    result = report.as_dict()

    prediction_drift = result['metrics'][0]['result']['drift_score']
    num_drifted_columns = result['metrics'][1]['result']['number_of_drifted_columns']
    share_missing_values = result['metrics'][2]['result']['current'][
        'share_of_missing_values'
    ]
    mask1 = f"insert into {METRIC_TABLE}"
    mask2 = "(timestamp, prediction_drift, num_drifted_columns, share_missing_values)"
    mask3 = "values (%s, %s, %s, %s)"
    query = mask1 + mask2 + mask3

    curr.execute(
        query,
        (
            begin + datetime.timedelta(i),
            prediction_drift,
            num_drifted_columns,
            share_missing_values,
        ),
    )


@flow
def batch_monitoring_backfill():
    """
    Performs batch monitoring backfill.

    This function prepares the database, connects to it, and calculates
      metrics for a range of values.
    It then sends the data and logs the information.

    Args:
        None

    Returns:
        None
    """
    prep_db()
    last_send = datetime.datetime.now() - datetime.timedelta(seconds=10)
    con = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
    with psycopg.connect(con, autocommit=True) as conn:
        for i in range(0, 5):
            with conn.cursor() as curr:
                calculate_metrics_postgresql(curr, i)

            new_send = datetime.datetime.now()
            seconds_elapsed = (new_send - last_send).total_seconds()
            if seconds_elapsed < SEND_TIMEOUT:
                time.sleep(SEND_TIMEOUT - seconds_elapsed)
            while last_send < new_send:
                last_send = last_send + datetime.timedelta(seconds=10)
            logging.info("data sent")
