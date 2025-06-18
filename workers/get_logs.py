import subprocess
import shlex
from config import WORKERS, DOCKER_COMPOSE_PATH, DOCKER_COMPOSE_CMD

def get_last_logs(worker_name):
    container = WORKERS[worker_name]['container_name']
    try:
        cmd_base = shlex.split(DOCKER_COMPOSE_CMD)
        cmd = cmd_base + ['-f', DOCKER_COMPOSE_PATH, 'logs', f'--tail=50', container]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout or "Sem logs disponíveis."
    except Exception as e:
        print(f"Erro ao obter logs: {e}")
        return "Erro ao obter logs."
