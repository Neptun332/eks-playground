from typing import Dict, List

from kubernetes import config, client
from kubernetes.client import V1Deployment

from ClusterClient import ClusterClient
from STSClient import STSClient


class K8sClient:

    def __init__(self, cluster_name: str, sts_client: STSClient, cluster_client: ClusterClient):
        self.cluster_info = cluster_client.get_cluster_info(cluster_name)
        bearer_token = sts_client.get_bearer_token_for_cluster(cluster_name)
        self.kubeconfig = self._get_cube_config(self.cluster_info, bearer_token)
        config.load_kube_config_from_dict(config_dict=self.kubeconfig)
        self.api_client = client.ApiClient()
        self.apps_v1_api = client.AppsV1Api(self.api_client)

    def create_deployments(self, deployments_body: List[V1Deployment], namespace: str = "default"):
        for deployment in deployments_body:
            print(f"Creating deployment: {deployment.metadata.name}")
            self.apps_v1_api.create_namespaced_deployment(body=deployment, namespace=namespace)

    def delete_all_deployments(self, namespace: str = "default"):
        deployments = self.apps_v1_api.list_namespaced_deployment(namespace=namespace)
        for deployment in deployments.items:
            deployment_name = deployment.metadata.name
            print(f"Deleting deployment: {deployment_name}")

            # Delete the deployment
            self.apps_v1_api.delete_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )

    def _get_cube_config(self, cluster: Dict[str, str], bearer_token: str) -> Dict:
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
