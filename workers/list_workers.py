import subprocess
import shlex
from config import WORKERS, DOCKER_COMPOSE_PATH, DOCKER_COMPOSE_CMD

def get_workers_status():
    status = {}
    try:
        cmd_base = shlex.split(DOCKER_COMPOSE_CMD)
        cmd = cmd_base + ['-f', DOCKER_COMPOSE_PATH, 'ps']

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout

        for name, config in WORKERS.items():
            container = config['container_name']
            # Container está "Up" se está rodando
            status[name] = False
            for line in output.splitlines():
                if container in line:
                    status[name] = "Up" in line
                    break

    except Exception as e:
        print(f"Erro ao obter status dos workers: {e}")
        for name in WORKERS:
            status[name] = False
    return status
