"Lambda function list pods in EKS cluster"
import logging

import boto3

from ClusterClient import ClusterClient
from HardcodedDeploymentTemplateProvider import HardcodedDeploymentTemplateProvider
from K8sClient import K8sClient
from STSClient import STSClient

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    "Lambda handler"
    streams = ["stream-1", "stream-2", "stream-3"]
    streams_newly_added = ["stream-1", "stream-2", "stream-3", "stream-4"]
    stream_to_delete = "stream-1"

    cluster_name = "fargate-cluster"
    session = boto3.session.Session()
    sts_client = STSClient(session)
    cluster_client = ClusterClient()
    k8s_client = K8sClient(cluster_name, sts_client, cluster_client)

    deployments = [HardcodedDeploymentTemplateProvider.create_deployment_template(name=steam_name)
                   for steam_name in streams]

    k8s_client.create_deployments(deployments)

    newly_added_deployments = [HardcodedDeploymentTemplateProvider.create_deployment_template(name=steam_name)
                   for steam_name in streams_newly_added]

    k8s_client.create_only_not_existing_deployments(newly_added_deployments)

    k8s_client.delete_deployment(stream_to_delete)

    k8s_client.delete_all_deployments()



print(handler(None, None))
