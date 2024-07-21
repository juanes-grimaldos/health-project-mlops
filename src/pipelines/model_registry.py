from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient
import logging
import logging
import mlflow

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
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
    
    @staticmethod
    def register_model(model_name):
        """
        Register a model in MLflow and transition its stage.

        Args:
            model_uri (str): The URI of the model to register.
            model_name (str): The name of the model.

        Returns:
            None
        """

        client = MlflowClient()

        experiment = client.get_experiment_by_name('random-forest')
        best_run = client.search_runs(
            experiment_ids=experiment.experiment_id,
            run_view_type=ViewType.ACTIVE_ONLY,
            max_results=1,
            order_by=["metrics.test_rmse ASC"]
        )[0]

        run_id = best_run.info.run_id

        best_run.data.metrics

        model_uri = f"runs:/{run_id}/model"
        best_run_test_rmse = best_run.data.metrics["rmse"]
        logging.info(f"Best Run Test RMSE:{best_run_test_rmse}")

        mlflow.register_model(model_uri=model_uri, name=model_name)
    
    @staticmethod
    def change_stage_model(model_name, new_stage, model_version):
        """
        Change the stage of a model in the model registry.

        Args:
            model_name (str): The name of the model.
            new_stage (str): The new stage to assign to the model. Must be one of: None, Staging, Production, Archived.
            model_version (str): The version of the model to update.

        Raises:
            ValueError: If the new_stage is not one of the valid stages.

        Returns:
            None
        """
        valid_stages = [None, "Staging", "Production", "Archived"]
        if new_stage not in valid_stages:
            raise ValueError("Invalid stage. Please choose one of: None, Staging, Production, Archived")

        client = MlflowClient()

        latest_versions = client.get_latest_versions(name=model_name)

        for version in latest_versions:
            logging.info(
                f"version: {version.version}, stage: {version.current_stage}"
                )

        
        client.transition_model_version_stage(
            name=model_name,
            version=model_version,
            stage=new_stage,
            archive_existing_versions=False
        )

        
        for version in latest_versions:
            logging.info(
                f"version: {version.version}, stage: {version.current_stage}"
                )
