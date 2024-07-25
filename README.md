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
source .venv/Scripts/activate
```

In this repository wer use MLflow locally, all data is store in SQLite. To generate the database, and run the server locally we need to run the code below on the terminal:
```bash
python -m mlflow server --backend-store-uri sqlite:///src/mlflow/mlflow.db --default-artifact-root ./artifacts_local
```

# Workflow
for this case I use Prefect, to run the flow, following this steps:
```bash
prefect server start
docker build -t workflow:1 -f workflow.Dockerfile 
docker run --network="host" -e PREFECT_API_URL=http://host.docker.internal:4200/api workflow:1
```

First I need to start the server, it could be locally or on a actual server.
Then a image is deploy in which all the workflow is deployed.
The deployment is set to run every 2 minutes, but it could be sent a run schedule with docker command.
