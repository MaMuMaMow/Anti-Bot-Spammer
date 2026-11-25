from db import asbyDb

async def delroom(guildId : int, chIds : int, cache : dict):
    if chIds not in cache[guildId]["chIds"]:
        return
    cache[guildId]["chIds"].remove(chIds)
    await asbyDb.remove_chId(guildId=guildId, chId=chIds)