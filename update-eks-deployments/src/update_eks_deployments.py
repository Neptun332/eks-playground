"Lambda function list pods in EKS cluster"
import base64
import logging
import os
import re

import boto3
from botocore.signers import RequestSigner
from kubernetes import client, config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

STS_TOKEN_EXPIRES_IN = 60
session = boto3.session.Session()
sts = session.client('sts')
service_id = sts.meta.service_model.service_id
cluster_name = "fargate-cluster"
eks = boto3.client('eks')
cluster_cache = {}


def get_cluster_info():
    "Retrieve cluster endpoint and certificate"
    cluster_info = eks.describe_cluster(name=cluster_name)
    endpoint = cluster_info['cluster']['endpoint']
    cert_authority = cluster_info['cluster']['certificateAuthority']['data']
    cluster_info = {
        "endpoint": endpoint,
        "ca": cert_authority,
        "ca_cert": str(base64.b64decode(cert_authority), "utf-8")
    }
    return cluster_info


def get_bearer_token():
    "Create authentication token"
    signer = RequestSigner(
        service_id,
        session.region_name,
        'sts',
        'v4',
        session.get_credentials(),
        session.events
    )

    params = {
        'method': 'GET',
        'url': 'https://sts.{}.amazonaws.com/'
               '?Action=GetCallerIdentity&Version=2011-06-15'.format(session.region_name),
        'body': {},
        'headers': {
            'x-k8s-aws-id': cluster_name
        },
        'context': {}
    }

    signed_url = signer.generate_presigned_url(
        params,
        region_name=session.region_name,
        expires_in=STS_TOKEN_EXPIRES_IN,
        operation_name=''
    )
    base64_url = base64.urlsafe_b64encode(signed_url.encode('utf-8')).decode('utf-8')

    # remove any base64 encoding padding:
    return 'k8s-aws-v1.' + re.sub(r'=*', '', base64_url)


def handler(_event, _context):
    "Lambda handler"
    if cluster_name in cluster_cache:
        cluster = cluster_cache[cluster_name]
    else:
        # not present in cache retrieve cluster info from EKS service
        cluster = get_cluster_info()
        # store in cache for execution environment resuse
        cluster_cache[cluster_name] = cluster

    bearer_token = get_bearer_token()

    kubeconfig = {
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

    # filepath = f"cluster.crt"
    # with open(filepath, "w+") as f:
    #     f.write(cluster["ca_cert"])

    config.load_kube_config_from_dict(config_dict=kubeconfig)

    configuration = client.Configuration()
    configuration.api_key['authorization'] = f"Bearer {bearer_token}"
    configuration.host = cluster["endpoint"]
    configuration.verify_ssl = False
    # configuration.ssl_ca_cert = filepath

    api_client = client.ApiClient(configuration)
    apps_v1_api = client.AppsV1Api(api_client)
    core_v1_api = client.CoreV1Api()
    print(f"api_client.configuration=={api_client.configuration.host}")
    print(f"api_client.configuration=={api_client.configuration.api_key}")
    print(f"api_client.configuration=={api_client.configuration.api_key_prefix}")
    print(f"configuration=={configuration.host}")
    print(f"configuration=={configuration.api_key}")
    print(f"configuration=={configuration.api_key_prefix}")


    ret = apps_v1_api.list_namespaced_deployment("default")
    # ret = core_v1_api.list_namespaced_pod("default")

    return f"There are {len(ret.items)} deployments in the default namespace."


print(handler(None, None))
