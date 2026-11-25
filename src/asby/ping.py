import discord
from logger.logger import log

async def ping(interaction: discord.Interaction, client : discord.Client):
    fromWhere = "/asby/ping.py/ping()"
    log(msg=f"/ping by user : {interaction.user}, ch : {interaction.channel}, server :{interaction.guild}", 
        evn=0,act=1, fromWhere=fromWhere)
    await interaction.response.send_message(f"Pong! {round(client.latency * 1000)}ms")