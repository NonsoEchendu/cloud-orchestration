import os
import git
from kubernetes_manager import KubernetesManager
import logging

k8s_manager = KubernetesManager()

async def deployment_workflow(user_id: str, repo_url: str):
    try:
        repo_path = clone_repository(repo_url, user_id)

        if not namespace_exists(user_id):
            k8s_manager.create_namespace(user_id)

        k8s_manager.deploy_test_pod(user_id, repo_path)
        logs = k8s_manager.get_logs(user_id)

        if "test passed" in logs:
            logging.info(f"Tests passed for {user_id}, deploying to production...")
            await deploy_to_production(user_id)
        else:
            logging.error(f"Tests failed for {user_id}. Logs: {logs}")
    except Exception as e:
        logging.error(f"Deployment error: {e}")

def clone_repository(repo_url: str, user_id: str) -> str:
    path = f"/repos/{user_id}"
    if os.path.exists(path):
        repo = git.Repo(path)
        repo.remotes.origin.pull()
    else:
        repo = git.Repo.clone_from(repo_url, path)
    return path

async def deploy_to_production(user_id: str):
    logging.info(f"Deploying {user_id} to production...")
    # Add Helm/YAML deployment logic here
