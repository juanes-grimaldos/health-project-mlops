# health-project-mlops

Estimating Time from Referral to Procurement using Organ Retrieval and Collection of Health Information for Donation from [physionet.org](https://doi.org/10.13026/b1c0-3506).
This project is linked with mlops datatalks first attempt to [MLOps Zoomcamp](https://github.com/DataTalksClub/mlops-zoomcamp) 2024 course!.


To download the data you need to run the following code. Note that you need to change the user to your credential: 

```bash
wget --user=USERNAME --ask-password -O src/data/referrals.csv https://physionet.org/files/orchid/2.0.0/referrals.csv
referrals.csv
```

```bash
source .venv/bin/activate
```

In this repository wer use MLflow locally, all data is store in SQLite. To generate the database, and run the server locally we need to run the code below on the terminal:
```bash
python -m mlflow server --backend-store-uri sqlite:///src/mlflow/mlflow.db --default-artifact-root ./artifacts_local
```

# Workflow
for this case I use Prefect.

```bash
prefect server start
python workflow.py
```

```bash
prefect config set PREFECT_API_URL="http://127.0.0.1:4200/api"
prefect profile use default
```