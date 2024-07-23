from hyperopt import STATUS_OK, Trials, fmin, hp, tpe
from hyperopt.pyll import scope
import mlflow
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

def run_optimization_rf(
    num_trials: int,
    X_train: pd.DataFrame, 
    y_train: pd.DataFrame, 
    X_val: pd.DataFrame, 
    y_val: pd.DataFrame):
    """
    Runs the optimization process for a Random Forest model.

    Parameters:
    - num_trials (int): The number of optimization trials to perform.
    - X_train (pd.DataFrame): The training data features.
    - y_train (pd.DataFrame): The training data labels.
    - X_val (pd.DataFrame): The validation data features.
    - y_val (pd.DataFrame): The validation data labels.
    """
    mlflow.set_tracking_uri("sqlite:///mlflow/mlflow.db")
    mlflow.set_experiment("random-forest")

    def objective(params):
        with mlflow.start_run():
            mlflow.log_params(params)
            rf = RandomForestRegressor(**params)
            rf.fit(X_train, y_train)
            y_pred = rf.predict(X_val)
            rmse = mean_squared_error(y_val, y_pred, squared=False)
            mlflow.log_metric("rmse", rmse)

        return {'loss': rmse, 'status': STATUS_OK}

    search_space = {
        'max_depth': scope.int(hp.quniform('max_depth', 1, 30, 1)),
        'n_estimators': scope.int(hp.quniform('n_estimators', 10, 100, 1)),
        'min_samples_split': scope.int(hp.quniform('min_samples_split', 2, 10, 1)),
        'min_samples_leaf': scope.int(hp.quniform('min_samples_leaf', 1, 4, 1)),
        'random_state': 42
    }

    rstate = np.random.default_rng(42)  # for reproducible results
    best_hyperparameters = fmin(
        fn=objective,
        space=search_space,
        algo=tpe.suggest,
        max_evals=num_trials,
        trials=Trials(),
        rstate=rstate
    )
    
    # fmin will return max_depth as a float for some reason
    for key in [
        'max_depth',
        'max_iter',
        'min_samples_leaf',
    ]:
        if key in best_hyperparameters:
            best_hyperparameters[key] = int(best_hyperparameters[key])
    
    return best_hyperparameters     
