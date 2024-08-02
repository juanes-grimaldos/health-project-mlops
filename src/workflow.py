import os
import logging

from prefect import flow, task

from pipelines.load_data import load_and_preprocess_data
from pipelines.model_registry import ModelRegistry
from pipelines.split_datasets import split_datasets
from pipelines.random_forest_track import run_optimization_rf


@task
def load_data():
    """
    Loads and preprocesses data, and splits it into datasets.

    Returns:
        datasets (list): A list of datasets containing the preprocessed data.
    """
    preprocessed_data = load_and_preprocess_data()
    datasets = split_datasets(preprocessed_data)
    return datasets


@task
def train_model(datasets):
    """
    Trains a model using the given datasets and returns the best hyperparameters.

    Args:
        datasets (dict): A dictionary containing the training and testing datasets.

    Returns:
        dict: A dictionary containing the best hyperparameters found during optimization.
    """
    best_hyperparameters = run_optimization_rf(
        10,
        datasets['X_train'],
        datasets['y_train'],
        datasets['X_test'],
        datasets['y_test'],
    )
    return best_hyperparameters


@task
def register_model(uri, experiment_name):
    """
    Register a model in the model registry.

    Args:
        uri (str): The tracking URI for the model registry.
        experiment_name (str): The name of the experiment.

    Returns:
        None
    """
    model_registry = ModelRegistry(tracking_uri=uri, experiment_name=experiment_name)
    model_registry.register_model("random-forest")


@flow
def workflow(
    mlflow_path: str = os.getenv("MLFLOW_URI"),
    experiment: str = "random-forest",
) -> None:
    """The main training pipeline"""
    datasets = load_data()
    best_hyper_params = train_model(datasets)
    logging.info("Best hyperparameters: %s", best_hyper_params)
    register_model(mlflow_path, experiment)
