import logging

import mlflow
from joblib import load
from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient
from mlflow.exceptions import MlflowException

logging.basicConfig(level=logging.INFO)


class ModelRegistry:
    def __init__(self, tracking_uri, experiment_name):
        """
        Initialize the ModelRegistry class.

        Args:
            tracking_uri (str): The URI of the MLflow tracking server.
            experiment_name (str): The name of the experiment to use.

        Returns:
            None
        """
        self.experiment = experiment_name
        self.tracking_uri = tracking_uri
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)

    def register_model(self, model_name):
        """
        Register a model in MLflow and transition its stage.

        Args:
            model_name (str): The name of the model.

        Returns:
            None
        """

        client = MlflowClient()

        experiment = client.get_experiment_by_name(self.experiment)
        best_run = client.search_runs(
            experiment_ids=experiment.experiment_id,
            run_view_type=ViewType.ACTIVE_ONLY,
            max_results=1,
            order_by=["metrics.rmse ASC"],
        )[0]
        model_uri = f"runs:/{best_run.info.run_id}/sklearn-model"
        best_run_test_rmse = best_run.data.metrics["rmse"]
        logging.info("Best Run Test RMSE: %s", str(best_run_test_rmse))
        mlflow.register_model(model_uri=model_uri, name=model_name)

    def get_model_version(self, model_name):
        """
        Get the version of a model in MLflow.

        Args:
            model_name (str): The name of the model.

        Raises:
            ValueError: If the new_stage is not one of the valid stages.

        Returns:
            None
        """

        client = MlflowClient(tracking_uri=self.tracking_uri)

        try:
            latest_versions = client.get_latest_versions(name=model_name)[0]
        except MlflowException as e:
            logging.error("Error occurred while getting latest versions: %s", str(e))
            path = 'start_models/random_forest.pkl'
            latest_versions = load(path)
            logging.info("Loaded model from path: %s", path)
            return latest_versions
        model_version = latest_versions.version
        model_uri = f"models:/{model_name}/{model_version}"
        model = mlflow.pyfunc.load_model(model_uri)
        return model
