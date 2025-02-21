from kubernetes import client, config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

class KubernetesManager:
    def __init__(self):
        config.load_kube_config()
        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.networking_v1 = client.NetworkingV1Api()

    def create_namespace(self, user_id: str):
        try:
            namespace = client.V1Namespace(
                metadata=client.V1ObjectMeta(name=user_id)
            )
            self.core_v1.create_namespace(namespace)
            logging.info(f"Namespace {user_id} created.")
        except client.exceptions.ApiException as e:
            if e.status == 409:
                logging.warning(f"Namespace {user_id} already exists.")
            else:
                logging.error(f"Failed to create namespace {user_id}: {e}")

    def deploy_test_pod(self, user_id: str, repo_path: str):
        try:
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
            logging.info(f"Pod {user_id}-test deployed in namespace {user_id}.")
        except client.exceptions.ApiException as e:
            logging.error(f"Failed to deploy pod {user_id}-test: {e}")

    def get_logs(self, user_id: str):
        try:
            pod_logs = self.core_v1.read_namespaced_pod_log(
                name=f"{user_id}-test", namespace=user_id
            )
            return pod_logs
        except client.exceptions.ApiException as e:
            logging.error(f"Failed to get logs for pod {user_id}-test: {e}")
            return None

# Example usage
if __name__ == "__main__":
    manager = KubernetesManager()
    user_id = "test-user"
    manager.create_namespace(user_id)
    manager.deploy_test_pod(user_id, "/path/to/repo")
    logs = manager.get_logs(user_id)
    if logs:
        print(logs)