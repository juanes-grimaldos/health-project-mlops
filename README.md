# health-project-mlops

Estimating Time from Referral to Procurement using Organ Retrieval and Collection of Health Information for Donation from [physionet.org](https://doi.org/10.13026/b1c0-3506).
This project is linked with mlops datatalks first attempt to [MLOps Zoomcamp](https://github.com/DataTalksClub/mlops-zoomcamp) 2024 course!.


# Load data
read -p "Enter your username: " username
wget -r -N -c -np --user "$username" --ask-password https://physionet.org/files/orchid/2.0.0/referrals.csv


# project
On this project you could upload to a cloud using docker compose up with the docker-compose.yml file on root directory.

```batch
docker-compose up
```
In case the workflow service is not running, run the container again

docker-compose -f docker-compose.gra.yml up --build

mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./artifacts --host 0.0.0.0 --port 5000cd


export COOKIE_API_REQUEST='_ga=GA1.2.263637740.1720827977; _ga_YKC8ZQQ4FF=GS1.1.1722094447.5.1.1722094879.0.0.0; csrftoken=dupoQ7jFXMN2dE6MrVvg2F08528jeroc; _gid=GA1.2.1133650335.1722094448; sessionid=nx4uuw1er9ox7aqf6gmld8cc2u2fkgzx'

export MLFLOW_URI=sqlite:///mlflow.db