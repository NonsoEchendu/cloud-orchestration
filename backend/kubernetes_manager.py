from kubernetes import client, config
import logging

class KubernetesManager:
    def __init__(self):
        config.load_kube_config()
        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.networking_v1 = client.NetworkingV1Api()

    def create_namespace(self, user_id: str):
        namespace = client.V1Namespace(
            metadata=client.V1ObjectMeta(name=user_id)
        )
        self.core_v1.create_namespace(namespace)
        logging.info(f"Namespace {user_id} created.")

    def deploy_test_pod(self, user_id: str, repo_path: str):
        container = client.V1Container(
            name="test-runner",
            image="python:3.9",
            command=["python", "/app/test_runner.py"],
            volume_mounts=[client.V1VolumeMount(
                name="code-volume",
                mount_path="/app"
            )]
        )

        pod = client.V1Pod(
            metadata=client.V1ObjectMeta(name=f"{user_id}-test", namespace=user_id),
            spec=client.V1PodSpec(containers=[container])
        )

        self.core_v1.create_namespaced_pod(namespace=user_id, body=pod)

    def get_logs(self, user_id: str):
        pod_logs = self.core_v1.read_namespaced_pod_log(
            name=f"{user_id}-test", namespace=user_id
        )
        return pod_logs
