import discord
from discord import app_commands
from logger.logger import log
from db import asbyDb,onReady

import os
import sys

async def clear_data(client : discord.Client, cache : dict):
    for guildId in list(cache):
        guild = client.get_guild(guildId)
        if guild is None:
            await asbyDb.delete_guild(guildId)
            cache.pop(guildId, None)
            continue

        if guild.unavailable:
            continue
        chIds = cache[guildId]["chIds"]
        alive = {c for c in chIds if guild.get_channel(c) is not None}

        if alive != chIds:
            await asbyDb.set_chIds(guildId=guildId, alive=list(alive))
            cache[guildId]["chIds"] = alive     

 
async def setup(tree : app_commands.CommandTree, client : discord.Client, cache : dict) -> int:
    """
    setup when start
    """
    fromWhere = "/asby/onReady.py/on_ready()"
    log(msg=f"calling /db/onReady.py/init()", evn=0,act=6, fromWhere=fromWhere)
    dsn = os.environ.get("DATABASE_URL", "")
        
    await onReady.init(dsn=dsn)

    #------- clear data and caching ----
    log(msg=f"calling /db/asbyDb.py/get_all_spam_rooms()", evn=0,act=6, fromWhere=fromWhere)
    cache.clear()
    cache.update(await asbyDb.get_all_spam_rooms())
    print(cache)
    log(msg=f"calling /asby/onReady.py/on_ready()", evn=0,act=6, fromWhere=fromWhere)
    await clear_data(client=client, cache=cache)
    print(cache)

    #------- synce commands ----
    log(msg=f"We have logged in as {client.user}", evn=1, fromWhere=fromWhere)
    log(msg=f"Bot is in {len(client.guilds)} server(s):", evn=1, fromWhere=fromWhere)
    try:
        synced = await tree.sync()
    except discord.HTTPException as e:
        log(msg=f"cannot sync commands: {e}", evn=3, fromWhere=fromWhere)
        return 1
    log(msg=f"Synced {len(synced)} slash command(s)", evn=1, fromWhere=fromWhere)
    
    if not synced:
        log(msg="0 commands synced — are they registered on the tree?", evn=2, fromWhere=fromWhere)
    return 0