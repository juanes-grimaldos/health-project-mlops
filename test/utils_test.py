from src.utils import smape
import numpy as np

def test_smape():
    y_true = np.array([1, 2, 3])
    y_pred = np.array([1, 2, 3])
    actual_result = smape(y_true, y_pred)

    expected_result = 0

    assert actual_result == expected_result