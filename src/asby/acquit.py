import discord
from logger.logger import log
from collections import OrderedDict

async def acquit(interaction : discord.Interaction, user : discord.User, susDict : dict):
    fromWhere = "/asby/acquit.py/acquit()"
    log(msg=f"user {interaction.user} user /acquit for user {user.name} in {interaction.guild}",
        evn=1,act=-1,fromWhere=fromWhere )

    print(susDict)
    susDict.pop((interaction.guild_id, user.id))

    try:    
        await interaction.guild.unban(user)
    except Exception as e:
        log(msg=f"cannot unban user {user.name} : {e}",evn=2,act=-1,fromWhere=fromWhere)
    
    try :
        await interaction.guild.get_member(user.id).timeout(None)
    except Exception as e:
        log(msg=f"cannot unmute user {user.name} : {e}",evn=2,act=-1,fromWhere=fromWhere)
    await interaction.response.send_message(f"acquited {user.name}")