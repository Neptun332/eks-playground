"Lambda function list pods in EKS cluster"
import logging
from typing import Dict

import boto3
from kubernetes import client, config

from ClusterClient import ClusterClient
from STSClient import STSClient

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_cube_config(cluster: Dict[str, str], bearer_token: str) -> Dict:
    return {
        'apiVersion': 'v1',
        'clusters': [{
            'name': 'cluster1',
            'cluster': {
                'certificate-authority-data': cluster["ca"],
                'server': cluster["endpoint"]}
        }],
        'contexts': [{'name': 'context1', 'context': {'cluster': 'cluster1', "user": "user1"}}],
        'current-context': 'context1',
        'kind': 'Config',
        'preferences': {},
        'users': [{'name': 'user1', "user": {'token': bearer_token}}]
    }


def handler(event, context):
    "Lambda handler"
    cluster_name = "fargate-cluster"
    session = boto3.session.Session()
    sts_client = STSClient(session)
    cluster_client = ClusterClient()

    cluster_info = cluster_client.get_cluster_info(cluster_name)
    bearer_token = sts_client.get_bearer_token_for_cluster(cluster_name)

    kubeconfig = get_cube_config(cluster_info, bearer_token)

    config.load_kube_config_from_dict(config_dict=kubeconfig)

    api_client = client.ApiClient()
    apps_v1_api = client.AppsV1Api(api_client)

    ret = apps_v1_api.list_namespaced_deployment("default")

    return f"There are {len(ret.items)} deployments in the default namespace."


print(handler(None, None))
