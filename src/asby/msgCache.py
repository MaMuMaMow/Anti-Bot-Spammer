from collections import OrderedDict,deque
import discord
import time
import os
import asyncio
from collections import defaultdict
from logger.logger import log

class userMsg :
    __slots__ = ("msgId", "time", "chId") 
    def __init__(self, msgId : int, time : float, chId : int):
        self.msgId = msgId
        self.time = time
        self.chId = chId

async def clear_msg_cahce(msgCache : OrderedDict[tuple[int,int], deque[userMsg]], settingsCache : dict):
    t = time.monotonic()
    
    for userId, guildId in list(msgCache) :
        key = (userId,guildId)
        dq = msgCache[(userId,guildId)]
        
        while (len(dq) > 0) and (dq[0].time - t > settingsCache[guildId]["msgCachingDuration"]) :
            dq.popleft()

        if len(dq) == 0 :
            msgCache[key].pop()
        else :
            msgCache[key]=dq

async def delete_in_ch(guild: discord.Guild, bot: discord.Client, chId: int, ids: list[int]):
    channel = guild.get_channel_or_thread(chId)
    if channel is None:
        try:
            channel = await bot.fetch_channel(chId)
        except (discord.NotFound, discord.Forbidden):
            return
    try:
        await channel.delete_messages([discord.Object(id=m) for m in ids])
    except discord.HTTPException as e:
        log(msg=f"delete failed in {chId}: {e}",evn=2,act=1,fromWhere="/asby/msgCache.py/delete_in_ch()")

async def delete_msg(guild : discord.Guild, userId : int, setting : dict, bot : discord.Client,
                     msgCache : OrderedDict[tuple[int,int], deque[userMsg]]):

    key = (userId,guild.id)
    msgInfo = msgCache[key]

    delMsg = defaultdict(list)

    catchTime = curTime = msgInfo[0].time
    count = 0

    for msg in msgInfo:
        t = msg.time
        if t - catchTime > setting["msgCacheDelTime"] or count >= setting["msgCacheDelAmount"]:
            break

        if t - curTime <= setting["timeGap"]:
            delMsg[msg.chId].append(msg.msgId)

        count += 1
        curTime = t

    await asyncio.gather(
        *(delete_in_ch(guild, bot, chId, ids) for chId, ids in delMsg.items())
    )


async def update_msg_cache(msgCache : OrderedDict[tuple[int,int], deque[userMsg]], 
                    settingsCache : dict, msg : discord.Message):

    guildId = msg.guild.id
    chId = msg.channel.id
    userId = msg.author.id
    msgId = msg.id
    cacheLimit = int(os.environ.get("MAX_MSG_CACHE",20000))
    
    key = (userId,guildId)

    if not settingsCache.get(guildId,False):
        return
    
    if not msgCache.get(key,False) :
        msgCache[key] = deque()
    
    while len(msgCache) > cacheLimit :
        msgCache.popitem(last=False)

    while (len(msgCache[key]) >= settingsCache[guildId]["msgCacheAmount"]):
        msgCache[key].pop()

    val = userMsg(msgId=msgId,time=time.monotonic(),chId=chId)
    msgCache[key].appendleft(val)
    msgCache.move_to_end(key=key)