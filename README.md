# README - Discord RabbitMQ Worker Manager Bot

---

## Descrição

Este bot Discord permite gerenciar e monitorar workers RabbitMQ rodando em containers Docker Compose.  
Funcionalidades principais:

- Listar workers e seu status (rodando ou parado)  
- Mostrar últimas 50 linhas de logs de um worker  
- Reiniciar workers (com permissão específica)  

---

## Pré-requisitos

- Python 3.10+  
- Docker Compose instalado no servidor  
- Token de bot do Discord  
- Cargo (role) no Discord para controlar permissão  

---

## Instalação

1. Clone o repositório:

```bash
git clone https://github.com/Jusizi/discord-rabbitmq.git
cd discord-rabbitmq
```

2. Crie e ative um ambiente virtual Python (opcional, mas recomendado):

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Crie um arquivo `.env` na raiz do projeto, com as variáveis necessárias (exemplo abaixo).

---

## Configuração

### Arquivo `.env`

```env
DISCORD_TOKEN=seu_token_do_bot_aqui
AUTHORIZED_ROLE=NomeDoCargoAutorizado

DOCKER_COMPOSE_PATH=/caminho/para/seu/docker-compose.yml

WORKERS_JSON={"NFSe Consulta":{"container_name":"worker-nfse-consulta"},"Boletos Consulta":{"container_name":"worker-boletos-consultas"}}
```

- **DISCORD_TOKEN:** Token do bot criado no [portal de desenvolvedores Discord](https://discord.com/developers/applications).
- **AUTHORIZED_ROLE:** Nome exato do cargo que terá permissão para reiniciar workers.
- **DOCKER_COMPOSE_PATH:** Caminho absoluto para o arquivo docker-compose.yml que gerencia os containers.
- **WORKERS_JSON:** JSON com os nomes dos workers e seus respectivos nomes de container Docker.

---

## Uso

### Comandos disponíveis (prefixo `!`)

| Comando            | Descrição                                            | Permissão              |
|--------------------|-----------------------------------------------------|------------------------|
| `!help`            | Mostra a lista de comandos disponíveis               | Todos                  |
| `!workers`         | Lista todos os workers cadastrados e seus status    | Todos                  |
| `!logs <worker>`   | Mostra as últimas linhas de log do worker            | Todos                  |
| `!restart <worker>`| Reinicia o worker especificado                        | Apenas cargos autorizados |

---

## Exemplo de comandos

```txt
!workers
!logs NFSe Consulta
!restart Boletos Consulta
```

---

## Executando o bot

```bash
python3 bot.py
```

---

## Segurança

- Apenas usuários com o cargo definido em `AUTHORIZED_ROLE` podem usar o comando `!restart`.
- O bot valida se o nome do worker existe antes de executar qualquer ação.
- Limite de cooldown de 10 segundos por usuário no comando `!restart` para evitar abusos.

---

## Como adicionar o bot ao seu servidor Discord

1. Vá para o [portal de desenvolvedores Discord](https://discord.com/developers/applications).  
2. Selecione seu bot ou crie um novo.  
3. Vá para a aba **OAuth2 > URL Generator**.  
4. Marque o escopo `bot` e as permissões `Send Messages` e `Read Message History`.  
5. Copie o link gerado e acesse para adicionar o bot ao seu servidor.  

---

## Dependências

- discord.py  
- python-dotenv

---




# Fazer do BOT um serviço Linux (Extra)

Criar a configuração do serviço
```bash
sudo nano /etc/systemd/system/discord-rabbitmq.service
```

Conteúdo
```service
[Unit]
Description=Discord RabbitMQ Bot
After=network.target

[Service]
User=root
WorkingDirectory=/home/discord-rabbitmq
ExecStart=/home/discord-rabbitmq/venv/bin/python /home/discord-rabbitmq/bot.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

Restartar os serviços
```bash
sudo systemctl daemon-reload
sudo systemctl enable discord-rabbitmq.service
sudo systemctl start discord-rabbitmq.service
```

Verificar se está rodando..
```bash
sudo service discord-rabbitmq status
```

## Contato / Suporte

Se precisar de ajuda, abra uma issue no repositório ou me chame no Discord.
