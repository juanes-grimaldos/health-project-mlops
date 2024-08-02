from prefect import serve

from workflow import workflow
from data_monitoring import batch_monitoring_backfill

if __name__ == "__main__":
    workflow_deploy = workflow.to_deployment(
        name='workflow',
        cron='*/15 * * * *',
        tags=['mlops', 'tracking'],
        description='keep track on the model performance',
        version='0.1.0',
    )
    monitoring_deploy = batch_monitoring_backfill.to_deployment(
        name='data_monitoring',
        cron='*/10 * * * *',
        tags=['evently', 'grafana'],
        description='monitor the data',
        version='0.1.0',
    )

    serve(workflow_deploy, monitoring_deploy)
