cat eksctl-cluster-config.yaml | envsubst '${ACCOUNT_NUMBER}' > eksctl-cluster-config.yaml
eksctl create cluster -f .\eksctl-cluster-config.yaml
