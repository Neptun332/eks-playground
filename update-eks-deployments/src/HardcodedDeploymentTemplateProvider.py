from kubernetes.client import V1Deployment, V1ObjectMeta, V1DeploymentSpec, V1LabelSelector, V1PodTemplateSpec, \
    V1PodSpec, V1Container


class HardcodedDeploymentTemplateProvider:

    @staticmethod
    def create_deployment_template(name: str):
        return V1Deployment(
            metadata=V1ObjectMeta(name=name),
            spec=V1DeploymentSpec(
                replicas=1,
                selector=V1LabelSelector(
                    match_labels={"environment": "test"}
                ),
                template=V1PodTemplateSpec(
                    metadata=V1ObjectMeta(
                        labels={"environment": "test"}
                    ),
                    spec=V1PodSpec(
                        containers=[
                            V1Container(
                                name="alpine",
                                image="alpine:latest",
                                command=["sleep", "3600"]
                            )
                        ]
                    )
                )
            )
        )
