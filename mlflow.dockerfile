FROM python:3.10-slim

RUN pip install mlflow==2.14.3

EXPOSE 5000


CMD ["mlflow", "server", \
    "--backend-store-uri", "sqlite:///mlflow.db", \
    "--default-artifact-root", "src/mlflow/artifacts", \
    "--host", "0.0.0.0", \
    "--port", "5000" \
]