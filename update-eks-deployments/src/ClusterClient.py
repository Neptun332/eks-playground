import boto3


class ClusterClient:

    def __init__(self):
        self.boto_eks_client = boto3.client('eks')

    def get_cluster_info(self, cluster_name: str):
        "Retrieve cluster endpoint and certificate"
        cluster_info = self.boto_eks_client.describe_cluster(name=cluster_name)
        endpoint = cluster_info['cluster']['endpoint']
        cert_authority = cluster_info['cluster']['certificateAuthority']['data']
        cluster_info = {
            "endpoint": endpoint,
            "ca": cert_authority,
        }
        return cluster_info
