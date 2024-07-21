from src.utils import smape
import numpy as np
import pandas as pd
import pytest
from src.pipelines.load_data import load_and_preprocess_data

def test_smape():
    y_true = np.array([1, 2, 3])
    y_pred = np.array([1, 2, 3])
    actual_result = smape(y_true, y_pred)

    expected_result = 0

    assert actual_result == expected_result

@pytest.fixture
def mock_pd_read_csv(mocker):
    """Mock pandas.read_csv to return test data."""
    mock = mocker.patch("pandas.read_csv")
    mock.return_value = pd.DataFrame(
        {
            "time_referred": pd.date_range("2023-01-01", periods=10000),
            "time_procured": pd.date_range("2023-01-05", periods=10000),
            "ABO_BloodType": ["A", "B", "AB", "O"] * 2500,
            "ABO_Rh": ["+", "-", "+", "-"] * 2500,
        }
    )
    return mock


def test_load_and_preprocess_data(mock_pd_read_csv):
    """Tests the load_and_preprocess_data function with mocks."""

    # Function call triggers mocked behavior
    df_model = load_and_preprocess_data()

    # 1. Check for expected columns presence
    expected_columns = set([
        "time_referred",
        "time_procured",
        "tr_time_format",
        "tp_time_format",
        "time_to_procurement",
        "ABO_BloodType",
        "ABO_Rh",
        "blood_type",
    ])
    assert set(df_model.columns) >= expected_columns

    # 3. time_to_procurement type
    assert pd.api.types.is_numeric_dtype(df_model["time_to_procurement"])

