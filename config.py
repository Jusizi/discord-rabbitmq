import os
import json
from dotenv import load_dotenv
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
AUTHORIZED_ROLE = os.getenv("AUTHORIZED_ROLE")

DOCKER_COMPOSE_CMD = os.getenv("DOCKER_COMPOSE_CMD", "docker compose")  # padrão para versões novas
DOCKER_COMPOSE_PATH = os.getenv("DOCKER_COMPOSE_PATH")

workers_raw = os.getenv("WORKERS_JSON", "{}")
try:
    WORKERS = json.loads(workers_raw)
except json.JSONDecodeError:
    WORKERS = {}
