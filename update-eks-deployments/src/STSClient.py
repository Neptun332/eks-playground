import base64
import re

from botocore.signers import RequestSigner


class STSClient:
    STS_TOKEN_EXPIRES_IN = 60

    def __init__(self, session):
        self.session = session
        self.sts = session.client('sts')

    def get_bearer_token_for_cluster(self, cluster_name: str):
        "Create authentication token"
        signer = RequestSigner(
            self.sts.meta.service_model.service_id,
            self.session.region_name,
            'sts',
            'v4',
            self.session.get_credentials(),
            self.session.events
        )

        params = {
            'method': 'GET',
            'url': 'https://sts.{}.amazonaws.com/'
                   '?Action=GetCallerIdentity&Version=2011-06-15'.format(self.session.region_name),
            'body': {},
            'headers': {
                'x-k8s-aws-id': cluster_name
            },
            'context': {}
        }

        signed_url = signer.generate_presigned_url(
            params,
            region_name=self.session.region_name,
            expires_in=self.STS_TOKEN_EXPIRES_IN,
            operation_name=''
        )
        base64_url = base64.urlsafe_b64encode(signed_url.encode('utf-8')).decode('utf-8')

        # remove any base64 encoding padding:
        return 'k8s-aws-v1.' + re.sub(r'=*', '', base64_url)
