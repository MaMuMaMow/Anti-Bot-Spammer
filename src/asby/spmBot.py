import discord
from logger.logger import log
from asby.punish import apply_punishment
from asby.msgCache import delete_msg
from collections import OrderedDict

in_progress = set()   # members currently being kicked
punishDict = {
    "ban" : "banned",
    "timeout" : "muted",
    "kick" : "kicked"
}

async def is_spam(message: discord.Message,settings : dict, susDict : dict[tuple[int,int],set], bot:discord.Client, msgCache : OrderedDict ):
    fromWhere = "/asby/punish.py/is_spam()"
    member = message.author
    guild = message.guild
    chId = message.channel.id

    if not settings.get(guild.id,""):
        return

    setting = settings[guild.id]
    susKey = (guild.id,member.id)

    if chId in setting["chIds"]:
        if not susDict.get(susKey,False):
            susDict[susKey] = {chId}
        else :
            if chId not in susDict[susKey]:
                susDict[susKey].add(chId)

    if len(susDict.get(susKey,[])) >= setting["minRooms"] :
        # Spam bots often send several messages at once - only handle each member once
        if member.id in in_progress:
            return
        in_progress.add(member.id)

        try:
            await delete_msg(guild=guild,userId=message.author.id,setting=settings[guild.id],bot=bot,msgCache=msgCache)

            try:
                await member.send(f"You were {punishDict[setting["punishment"]]} from **{guild.name}** for typing in the spam channel.")
            except discord.HTTPException:
                pass

            await apply_punishment(punishment=setting["punishment"],guild=guild,
                                   member=member,timeout=setting["timeoutDuration"])
            susDict.pop(susKey,"")

        except discord.Forbidden:
            log(msg=f"Missing permission to punish {member} in {guild}", evn=3, act=0, fromWhere=fromWhere)
        except discord.HTTPException as e:
            log(msg=f"Failed to punish {member}: {e}", evn=3, act=0, fromWhere=fromWhere)
        finally:
            in_progress.discard(member.id)