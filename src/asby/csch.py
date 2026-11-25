import discord
from logger.logger import log
from db import asbyDb

import discord

async def get_spm_msg() -> tuple[discord.Embed, discord.ui.View]:
    embed = discord.Embed(
        title="Anti-spam channel",
        description=(
            "This channel is used to catch spam bots.\nwhoever send any message here will get a softban."
        ),
        color=discord.Color.red(),     # colour of the left bar; remove for none
    )
    view = discord.ui.View(timeout=None)
    return embed, view

async def csch(interaction : discord.interactions, cache : dict) -> dict:
    fromWhere = "/asby/csch.py/ping()"

    guild = interaction.guild

    settings = dict(cache.get(guild.id,""))
    if ( settings and len(settings.get("chIds",[])) >= 10):
        await interaction.response.send_message(f"Asby can create only 10 room, no more than that!")
        return

    user = interaction.user
    ch = await guild.create_text_channel("spm")
    chId = ch.id
    
    if not cache.get(guild.id,None) :
        await asbyDb.add_chId(guildId=guild.id, chIds=chId)
        cache[guild.id] = {
            "chIds" : {chId},
            "minRooms" : 1
        }
    else :
        await asbyDb.add_chId(guildId=guild.id, chIds=chId, minRooms=cache[guild.id]["minRooms"] )
        cache[guild.id]["chIds"].add(chId)
    
    d = await asbyDb.get_all_spam_rooms()
    print(d)
    
    log(msg=f"/csch by user : {user}, ch : {chId}, server :{guild}", 
        evn=0,act=1, fromWhere=fromWhere)
    log(msg=f"created ch {ch.id} (#{interaction.channel}) in server {interaction.guild}",
        evn=1,act=0, fromWhere=fromWhere)

    embed, view = await get_spm_msg()
    await ch.send(embed=embed, view=view)
    
    await interaction.response.send_message(f"created {ch.mention}")