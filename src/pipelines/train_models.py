from sklearn.model_selection import train_test_split
from pipelines.load_data import load_and_preprocess_data
import pandas as pd

def train_models() -> dict:
    """
    Trains a model using the preprocessed data.

    Returns:
    - result: A dictionary containing the training and testing dataframes
    """

    features = [
        'Age', 'Gender', 'Race', 'HeightIn', 
        'WeightKg', 'blood_type', 'brain_death'
    ]

    df_model = load_and_preprocess_data()

    X = pd.get_dummies(df_model[features], drop_first=True)
    y = df_model['time_to_procurement']

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    result = {
        'X_train': X_train,
        'X_test': X_test,
        'y_train': y_train,
        'y_test': y_test
    }
    
    return result
