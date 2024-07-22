import pandas as pd
from sklearn.model_selection import train_test_split
if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

@data_exporter
def export_data(data, *args, **kwargs):
    """
    Exports data to some source.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Output (optional):
        Optionally return any object and it'll be logged and
        displayed when inspecting the block run.
    """
    # Specify your data exporting logic here

    features = [
        'Age', 'Gender', 'Race', 'HeightIn', 
        'WeightKg', 'blood_type', 'brain_death'
    ]

    df_model = data

    X = pd.get_dummies(df_model[features], drop_first=True)
    y = df_model['time_to_procurement']

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Returning data as a dictionary
    return {
        'X_train': X_train,
        'X_test': X_test,
        'y_train': y_train,
        'y_test': y_test
    }
