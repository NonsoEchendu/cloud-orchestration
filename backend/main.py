from fastapi import FastAPI, WebSocket, HTTPException
import json
import logging
from kubernetes import config, client
from gitlab_integration import process_webhook
from kubernetes_manager import KubernetesManager
from deployment_pipeline import deployment_workflow

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# Load Kubernetes config
config.load_kube_config()
k8s_manager = KubernetesManager()

# WebSocket connections pool
active_connections = {}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    active_connections[user_id] = websocket

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)

            if data['type'] == 'deploy':
                await deployment_workflow(user_id, data['repo_url'])
            elif data['type'] == 'get_logs':
                await k8s_manager.get_logs(user_id)
    except Exception as e:
        logging.error(f"WebSocket Error: {e}")
    finally:
        del active_connections[user_id]

@app.post("/webhook/gitlab")
async def gitlab_webhook(payload: dict):
    return await process_webhook(payload)
