from hyperopt import STATUS_OK, Trials, fmin, hp, tpe
from hyperopt.pyll import scope
import mlflow
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_squared_error
from pipelines.train_models import train_models

def run_optimization_xgb(
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
    mlflow.set_experiment("xgboost")

    def objective(params):
        with mlflow.start_run():
            mlflow.log_params(params)
            rf = xgb.XGBRegressor(**params)
            rf.fit(X_train, y_train)
            y_pred = rf.predict(X_val)
            rmse = mean_squared_error(y_val, y_pred, squared=False)
            mlflow.log_metric("rmse", rmse)

        return {'loss': rmse, 'status': STATUS_OK}
    
    search_space = {
        'objective': hp.choice('objective', ['reg:squarederror', 'reg:linear', 'reg:logistic']),  
        'max_depth': scope.int(hp.quniform('max_depth', 3, 12, 1)),  # Adjust range for better handling of skewness
        'n_estimators': scope.int(hp.quniform('n_estimators', 100, 1000, 1)),  # Increase for potentially more complex models
        'learning_rate': hp.uniform('learning_rate', 0.01, 0.3),  # Consider lower rates for skewed targets
        'gamma': hp.uniform('gamma', 0, 5),  # Handle overfitting and improve regularization
        'min_child_weight': scope.int(hp.quniform('min_child_weight', 3, 10, 1)),  # Adjust for data sparsity
        'subsample': hp.uniform('subsample', 0.5, 1),
        'colsample_bytree': hp.uniform('colsample_bytree', 0.5, 1),
        'reg_lambda': hp.uniform('reg_lambda', 0.1, 10),  # L2 regularization for stability
        'reg_alpha': hp.uniform('reg_alpha', 0, 1),  # L1 regularization for sparsity (optional)
        'enable_categorical': True,  # Enable for categorical feature handling
        'lambda_bias': hp.uniform('lambda_bias', 0, 1),  # Bias regularization (optional)
        'tree_method': hp.choice('tree_method', ['hist', 'approx']),
        'max_delta_step': scope.int(hp.quniform('max_delta_step', 0, 20, 1)),
    }


    rstate = np.random.default_rng(42)  # for reproducible results
    fmin(
        fn=objective,
        space=search_space,
        algo=tpe.suggest,
        max_evals=num_trials,
        trials=Trials(),
        rstate=rstate
    )

# Load and preprocess data
result = train_models()

run_optimization_xgb(
    10, result['X_train'], result['y_train'], 
    result['X_test'], result['y_test']
)