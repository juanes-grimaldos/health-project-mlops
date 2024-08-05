import os

import pandas as pd
from flask import Flask, jsonify, request

from pipelines.model_registry import ModelRegistry

app = Flask('health-project')

uri = os.getenv("MLFLOW_URI")
experiment_name = "random-forest"

model_registry = ModelRegistry(tracking_uri=uri, experiment_name=experiment_name)
model = model_registry.get_model_version("random-forest")

features = [
    "Age",
    "HeightIn",
    "WeightKg",
    "brain_death",
    "Gender_M",
    "Race_Hispanic",
    "Race_Other / Unknown",
    "Race_White / Caucasian",
    "blood_type_A-Negative ",
    "blood_type_A-Positive",
    "blood_type_A-Positive ",
    "blood_type_A1-Negative",
    "blood_type_A1-Negative ",
    "blood_type_A1-Positive",
    "blood_type_A1-Positive ",
    "blood_type_A1B-Negative",
    "blood_type_A1B-Negative ",
    "blood_type_A1B-Positive",
    "blood_type_A1B-Positive ",
    "blood_type_A2-Negative",
    "blood_type_A2-Negative ",
    "blood_type_A2-Positive",
    "blood_type_A2-Positive ",
    "blood_type_A2B-Negative",
    "blood_type_A2B-Positive",
    "blood_type_A2B-Positive ",
    "blood_type_AB-Negative",
    "blood_type_AB-Negative ",
    "blood_type_AB-Positive",
    "blood_type_AB-Positive ",
    "blood_type_B-Negative",
    "blood_type_B-Negative ",
    "blood_type_B-Positive",
    "blood_type_B-Positive ",
    "blood_type_O-Negative",
    "blood_type_O-Negative ",
    "blood_type_O-Positive",
    "blood_type_O-Positive ",
]


@app.route('/predict', methods=['POST'])
def predict_endpoint():
    """
    Endpoint for making predictions using the model.
    Returns:
        A JSON response containing the prediction result.
    Raises:
        ValueError: If more than one blood type is defined.
    """

    values = request.get_json()

    # Check if blood_type is defined for more than one
    blood_types = [key for key in values.keys() if key.startswith("blood_type")]
    if sum(values[blood_type] for blood_type in blood_types) > 1:
        return jsonify({'error': 'Only one blood type should be defined.'}), 400

    # Predict using the model
    prediction = model.predict(pd.DataFrame([values], columns=features))
    return jsonify({'prediction': prediction.tolist()})


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)
