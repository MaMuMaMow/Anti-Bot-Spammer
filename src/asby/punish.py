import discord
import datetime
from logger.logger import log

async def ban(guild : discord.Guild, member : discord.Member,reason:str):
    fromWhere = "/asby/punish.py/ban()"
    await member.ban(reason=reason)
    await member.send(f"You got banned from {guild} for sending a message in spam channel")
    log(msg=f"banned {member} from {guild}",evn=1,act=5,fromWhere=fromWhere)

async def kick(guild : discord.Guild, member : discord.Member,reason:str):
    fromWhere = "/asby/punish.py/kick()"
    await member.kick(reason=reason)
    await member.send(f"You got kicked out from {guild} for sending a message in spam channel")
    log(msg=f"kicked {member} from {guild}",evn=1,act=4,fromWhere=fromWhere)

async def mute(guild : discord.Guild, member : discord.Member,reason:str, 
               second : int=0):
    fromWhere = "/asby/punish.py/mute()"
    duration = datetime.timedelta(seconds=second)
    await member.timeout(duration,reason=reason)
    await member.send(f"You got timed out in {guild} for {duration} from sending a message in spam channel")
    log(msg=f"muted {member} from {guild}",evn=1,act=3,fromWhere=fromWhere)

async def apply_punishment(punishment : str, guild : discord.Guild,
                        member : discord.Member, timeout : int):
    reason = "send a message in spam channel."
    fromWhere = "/asby/punish.py/apply_punishment()"
    
    if punishment == "timeout":
        await mute(guild=guild, member=member, reason=reason, second=timeout)
    elif punishment == "kick":
        kick(guild=guild,member=member,reason=reason)
    elif punishment == "ban":
        ban(guild=guild,member=member,reason=reason)
    else :
        log(msg=f"unknow value for punishment {punishment}",evn=3,act=-1,fromWhere=fromWhere)