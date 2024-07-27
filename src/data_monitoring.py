import psycopg
import logging
from prefect import task, flow
import datetime
import random
from evidently.report import Report
from evidently import ColumnMapping
from evidently.metrics import ColumnDriftMetric, DatasetDriftMetric, DatasetMissingValuesMetric
from pipelines.model_registry import ModelRegistry
from pipelines.split_datasets import split_datasets
from pipelines.load_data import load_and_preprocess_data
import time

logging.basicConfig(
	level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s"
)
SEND_TIMEOUT = 10
rand = random.Random()

create_table_statement = """
drop table if exists dummy_metrics;
create table dummy_metrics(
	timestamp timestamp,
	prediction_drift float,
	num_drifted_columns integer,
	share_missing_values float
)
"""


uri = "sqlite:///mlflow.db"
experiment_name = "random-forest"

model_registry = ModelRegistry(
        tracking_uri=uri,
        experiment_name=experiment_name
    )
model = model_registry.get_model_version("random-forest")

data = load_and_preprocess_data()
val_data = split_datasets(data)['X_test']
train_data = split_datasets(data)['X_train']

begin = datetime.datetime(2022, 2, 1, 0, 0)
num_features = val_data.select_dtypes(include=['object', 'bool']).columns.tolist()
cat_features = val_data.select_dtypes(include=['float64', 'int64']).columns.tolist()
column_mapping = ColumnMapping(
    prediction='prediction',
    numerical_features=num_features,
    categorical_features=cat_features,
    target=None
)

report = Report(metrics = [
    ColumnDriftMetric(column_name='prediction'),
    DatasetDriftMetric(),
    DatasetMissingValuesMetric()
])

@task
def prep_db():
	"""
	generate a database and table for the dummy metrics
	"""
	connection = "host=localhost port=5432 user=postgres password=example"
	var = "host=localhost port=5432 dbname=test user=postgres password=example"
	with psycopg.connect(connection, autocommit=True) as conn:
		res = conn.execute("SELECT 1 FROM pg_database WHERE datname='test'")
		if len(res.fetchall()) == 0:
			conn.execute("create database test;")
		with psycopg.connect(var) as conn:
			conn.execute(create_table_statement)

@task
def calculate_metrics_postgresql(curr, i):
	# TODO: prediction column somehow appears before the model is trained
	val_data['prediction'] = model.predict(val_data)
	train_data['prediction'] = model.predict(train_data)

	report.run(reference_data = train_data, current_data = val_data,
		column_mapping=column_mapping)

	result = report.as_dict()

	prediction_drift = result['metrics'][0]['result']['drift_score']
	num_drifted_columns = result['metrics'][1]['result']['number_of_drifted_columns']
	share_missing_values = result['metrics'][2]['result']['current']['share_of_missing_values']

	curr.execute(
		"insert into dummy_metrics(timestamp, prediction_drift, num_drifted_columns, share_missing_values) values (%s, %s, %s, %s)",
		(begin + datetime.timedelta(i), prediction_drift, num_drifted_columns, share_missing_values)
	)

@flow
def batch_monitoring_backfill():
	prep_db()
	last_send = datetime.datetime.now() - datetime.timedelta(seconds=10)
	con = "host=localhost port=5432 dbname=test user=postgres password=example"
	with psycopg.connect(con, autocommit=True) as conn:
		for i in range(0, 27):
			with conn.cursor() as curr:
				calculate_metrics_postgresql(curr, i)

			new_send = datetime.datetime.now()
			seconds_elapsed = (new_send - last_send).total_seconds()
			if seconds_elapsed < SEND_TIMEOUT:
				time.sleep(SEND_TIMEOUT - seconds_elapsed)
			while last_send < new_send:
				last_send = last_send + datetime.timedelta(seconds=10)
			logging.info("data sent")

if __name__ == '__main__':
	batch_monitoring_backfill()