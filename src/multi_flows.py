from prefect import serve
from workflow import workflow
from data_monitoring import data_monitoring


if __name__ == "__main__":
    task1_deploy = workflow.to_deployment(
        name='workflow',
        cron='*/15 * * * *',
        tags=['mlops', 'tracking'],
        description='keep track on the model performance',
        version='0.1.0')
    task2_deploy = data_monitoring.to_deployment(
        name='data_monitoring',
        cron='*/10 * * * *',
        tags=['evently', 'grafana'],
        description='monitor the data',
        version='0.1.0')
    serve(
        task1_deploy,
        task2_deploy,
    )