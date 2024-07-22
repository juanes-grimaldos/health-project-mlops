from project.utils.models.sklearn import run_optimization_rf

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer


@transformer
def transform(data, *args, **kwargs):
    # Extract the training data
    X_train = data['export_ti_split_20_'][0]['X_train']
    y_train = data['export_ti_split_20_'][0]['y_train']  # Assumed this variable based on the context

    # Extract the validation data
    X_test = data['export_ti_split_20_'][0]['X_test']
    y_test = data['export_ti_split_20_'][0]['y_test']  # Assumed this variable based on the context

    # Run the optimization for random forest hyperparameters
    hyperparameters = run_optimization_rf(
        num_trials=10,
        X_train=X_train, 
        y_train=y_train, 
        X_val=X_test, 
        y_val=y_test
    )

    return hyperparameters
