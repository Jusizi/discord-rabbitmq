import shlex
import subprocess
from config import DOCKER_COMPOSE_CMD, WORKERS, DOCKER_COMPOSE_PATH

def restart_worker(worker_name):
    container = WORKERS[worker_name]['container_name']
    # Converte a string para lista (ex: 'docker compose' vira ['docker', 'compose'])
    cmd_base = shlex.split(DOCKER_COMPOSE_CMD)
    cmd = cmd_base + ['-f', DOCKER_COMPOSE_PATH, 'restart', container]

    try:
        subprocess.run(cmd, check=True)
        return "Reiniciado com sucesso!"
    except subprocess.CalledProcessError as e:
        try:
            subprocess.run(
                [DOCKER_COMPOSE_CMD, '-f', DOCKER_COMPOSE_PATH, 'up', '-d', container],
                check=True
            )
            return "✅ Container estava parado (scale=0), mas foi iniciado com sucesso!"
        except subprocess.CalledProcessError as e:
            return f"❌ Falha ao reiniciar ou subir o worker: {e}"
