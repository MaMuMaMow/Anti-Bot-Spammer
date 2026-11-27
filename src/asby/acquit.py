import discord
from logger.logger import log
from collections import OrderedDict

async def acquit(interaction : discord.Interaction, userId : int, susDict : dict):
    fromWhere = "/asby/acquit.py/acquit()"
    log(msg=f"user {interaction.user} user /acquit for user {userId} in {interaction.guild}",
        evn=1,act=-1,fromWhere=fromWhere )

    print(susDict)
    susDict.pop((interaction.guild_id, userId),"")

    res = ""
    try:    
        await interaction.guild.unban(discord.Object(id=userId))
    except discord.NotFound :
        pass
    except discord.Forbidden :
        res += f"cannot unban user {userId}, missing permission\n"
    except Exception as e:
        log(msg=f"cannot unban user {userId} : {e}",evn=2,act=-1,fromWhere=fromWhere)
    
    try :
        await interaction.guild.get_member(userId).timeout(None)
    except discord.Forbidden :
            res += f"cannot unmute user {userId}, missing permission\n"
    except Exception as e:
        log(msg=f"cannot unmute user {userId} : {e}",evn=2,act=-1,fromWhere=fromWhere)

    res += f"acquited userId : {userId}"
    await interaction.response.send_message(res,ephemeral=True)