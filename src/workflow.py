import os
from prefect import task, flow
from pipelines.load_data import load_and_preprocess_data
from pipelines.split_datasets import split_datasets
from pipelines.random_forest_track import run_optimization_rf
from pipelines.model_registry import ModelRegistry
import logging

@task
def load_data():
    preprocessed_data = load_and_preprocess_data()
    datasets = split_datasets(preprocessed_data)
    return datasets

@task
def train_model(datasets):
    best_hyperparameters = run_optimization_rf(
        10, 
        datasets['X_train'], 
        datasets['y_train'], 
        datasets['X_test'], 
        datasets['y_test']
    )
    return best_hyperparameters
    # TODO: we monitor the data here

@task
def register_model(uri, experiment_name):
    # TODO: in case the model has not improved, we should not register it
    model_registry = ModelRegistry(
        tracking_uri=uri,
        experiment_name=experiment_name
    )
    model_registry.register_model("random-forest")

@flow
def workflow(
    mlflow_path: str = os.getenv("MLFLOW_URI"),
    experiment: str = "random-forest",
) -> None:
    """The main training pipeline"""
    datasets = load_data()
    best_hyper_params = train_model(datasets)
    logging.info(f"Best hyperparameters: {best_hyper_params}")
    register_model(mlflow_path, experiment)
