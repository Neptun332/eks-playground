"Lambda function list pods in EKS cluster"
import logging
from typing import List

import boto3

from ClusterClient import ClusterClient
from HardcodedDeploymentTemplateProvider import HardcodedDeploymentTemplateProvider
from K8sClient import K8sClient
from STSClient import STSClient

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def delete_deployments_other_than(k8s_client: K8sClient, deployments_to_leave: List[str], namespace: str = "default"):
    deployments_names = k8s_client.get_deployments_names(namespace)
    for deployment_name in deployments_names:
        if deployment_name not in deployments_to_leave:
            k8s_client.delete_deployment(
                name=deployment_name,
                namespace=namespace
            )


def handler(event, context):
    "Lambda handler"
    streams = ["stream-1", "stream-2", "stream-3"]
    streams_newly_added = [
        "stream-1", "stream-2", "stream-3", "stream-4", "stream-5", "stream-6", "stream-7",
        "stream-8", "stream-9", "stream-10", "stream-11", "stream-12", "stream-13", "stream-14",
        "stream-15", "stream-16"
    ]
    stream_to_delete = "stream-1"

    cluster_name = "my-cluster"
    session = boto3.session.Session()
    sts_client = STSClient(session)
    cluster_client = ClusterClient()
    k8s_client = K8sClient(cluster_name, sts_client, cluster_client)

    # deployments = [HardcodedDeploymentTemplateProvider.create_deployment_template(name=steam_name)
    #                for steam_name in streams]
    #
    # k8s_client.create_deployments(deployments)
    #
    # newly_added_deployments = [HardcodedDeploymentTemplateProvider.create_deployment_template(name=steam_name)
    #                            for steam_name in streams_newly_added]
    #
    # k8s_client.create_only_not_existing_deployments(newly_added_deployments)

    # k8s_client.delete_deployment(stream_to_delete)
    #
    k8s_client.delete_all_deployments()


print(handler(None, None))
