import discord
from discord.ext import commands
from config import DISCORD_TOKEN, WORKERS, AUTHORIZED_ROLE
from workers.list_workers import get_workers_status
from workers.get_logs import get_last_logs
from workers.restart_worker import restart_worker
from discord.ext import commands

import os, io, asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

AUTHORIZED_ROLES = [r.strip().lower() for r in os.getenv("AUTHORIZED_ROLES", "").split(",")]

# Armazena o mapping: mensagem.id -> worker_name
worker_messages = {}

def is_authorized(ctx):
    user_roles = [role.name.lower() for role in ctx.author.roles]
    return any(role in user_roles for role in AUTHORIZED_ROLES)

def user_is_authorized(user):
    user_roles = [role.name.lower() for role in user.roles]
    return any(role in user_roles for role in AUTHORIZED_ROLES)

async def send_long_message(ctx, message: str):
    chunk_size = 1990  # 2000 - margem para os backticks e possíveis quebras
    for i in range(0, len(message), chunk_size):
        await ctx.send(f"```{message[i:i+chunk_size]}```")

@bot.command(name='help')
async def help_command(ctx):
    embed = discord.Embed(
        title="Comandos disponíveis 🤖",
        description="Veja abaixo os comandos que você pode usar com este bot:",
        color=discord.Color.blue()
    )
    embed.add_field(name="!workers", value="Lista todos os workers e seus status", inline=False)
    embed.add_field(name="!logs <worker>", value="Mostra as últimas 50 linhas de log do worker", inline=False)
    embed.add_field(name="!restart <worker>", value="Reinicia o worker (requer cargo autorizado)", inline=False)
    await ctx.send(embed=embed)

@bot.command(name='workers')
async def list_workers(ctx):
    status = get_workers_status()

    total_workers = len(status)
    atual = 0
    for worker_name, is_running in status.items():
        estado = '🟢 Rodando' if is_running else '🔴 Parado'
        atual += 1
        msg = await ctx.send(f"{atual}/{total_workers} **{worker_name}**\nStatus: {estado}")
        worker_messages[msg.id] = worker_name
        await msg.add_reaction('🔄')
        await asyncio.sleep(0.5)  # espera meio segundo entre as reações
        await msg.add_reaction('📄')
        await asyncio.sleep(0.5)  # mais um intervalo para evitar flood
    
    await ctx.send("Reaja com 🔄 para reiniciar ou 📄 para ver os logs do worker.")

@bot.command(name='logs')
async def show_logs(ctx, worker_name: str):
    worker_name = worker_name.lower()
    valid_workers = {k.lower(): k for k in WORKERS}
    
    if worker_name not in valid_workers:
        return await ctx.send("❌ Worker inválido ou não registrado.")
    
    original_name = valid_workers[worker_name]
    logs = get_last_logs(original_name)
    if not logs.strip():
        return await ctx.send(f"ℹ️ Nenhum log encontrado para `{original_name}`.")
    
    file = io.StringIO(logs)
    await ctx.send(file=discord.File(fp=file, filename=f"{original_name}_logs.txt"))

@bot.command(name='restart')
@commands.cooldown(1, 10, commands.BucketType.user)  # 1 uso a cada 10s por user
async def restart(ctx, worker_name: str):
    if not is_authorized(ctx):
        return await ctx.send("🚫 Você não tem permissão para isso.")

    worker_name = worker_name.lower()
    valid_workers = {k.lower(): k for k in WORKERS}
    
    if worker_name not in valid_workers:
        return await ctx.send("❌ Worker inválido ou não registrado.")

    original_name = valid_workers[worker_name]

    await ctx.send(f"🔁 Reiniciando `{original_name}`...")

    result = restart_worker(original_name)
    await ctx.send(f"🔁 Reinício de `{original_name}`: {result}")


@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    message_id = reaction.message.id
    emoji = reaction.emoji

    if message_id not in worker_messages:
        return  # reação não em mensagem de worker listada

    worker_name = worker_messages[message_id]

    if emoji == '🔄':

        if not user_is_authorized(user):
            await reaction.message.channel.send(f"🚫 {user.mention}, você não tem permissão para reiniciar workers.")
            return

        await reaction.message.channel.send(f"🔁 Reiniciando worker `{worker_name}` solicitado por {user.mention}...")
        resultado = restart_worker(worker_name)
        await reaction.message.channel.send(f"Resultado do restart: {resultado}")

    elif emoji == '📄':
        logs = get_last_logs(worker_name)
        if not logs.strip():
            await reaction.message.channel.send(f"ℹ️ Nenhum log encontrado para `{worker_name}`.")
        else:
            await reaction.message.channel.send(f"Logs do `{worker_name}`:", file=discord.File(fp=io.StringIO(logs), filename=f"{worker_name}_logs.txt"))

    # Remove a reação do usuário para poder usar novamente
    try:
        await reaction.remove(user)
    except discord.Forbidden:
        pass

@bot.event
async def on_command(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("Comandos só podem ser usados no servidor.")
        return

@bot.command(name='restart_all')
@commands.cooldown(1, 30, commands.BucketType.user)
async def restart_all(ctx):
    if not is_authorized(ctx):
        return await ctx.send("🚫 Você não tem permissão para isso.")

    await ctx.send("🔁 Reiniciando todos os workers...")

    results = []
    for worker_name in WORKERS:
        result = restart_worker(worker_name)
        results.append(f"**{worker_name}**: {result}")

    msg = "\n".join(results)
    await send_long_message(ctx, msg)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Comando em cooldown. Tente novamente em {error.retry_after:.1f} segundos.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❗ O argumento `{error.param.name}` é obrigatório para o comando `{ctx.command}`.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Comando não encontrado. Use `!help` para ver os comandos disponíveis.")
    else:
        raise error  # relança outras exceções

bot.run(DISCORD_TOKEN)
