from project.utils.models.sklearn import run_optimization_rf

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer


@transformer
def hyperparameter_tuning(
    training_set,
    *args,
    **kwargs):

    result = training_set['export_ti_split_20_'][0]

    hyperparameters = run_optimization_rf(
        X_train=result['X_train'],
        y_train=result['y_train'],
        X_val=result['X_test'],
        y_val=result['y_test'],
        num_trials=kwargs.get('max_evaluations'),
    )

    return hyperparameters