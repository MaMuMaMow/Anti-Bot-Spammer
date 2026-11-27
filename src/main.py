import discord
import os
import sys
from discord import app_commands
from discord.ext.commands import has_permissions, CheckFailure
from collections import OrderedDict
from discord.ext import tasks

from logger.logger import log
import asby.onReady
import asby.ping
import asby.csch
import asby.delroom
import asby.msgCache
from asby.spmBot import is_spam
from asby.acquit import acquit as aq
from asby.config import SettingsPanel

class Asby:
    def __init__(self):
        self.intent = discord.Intents.default()
        self.intent.message_content = True
        self.intent.members = True
        self.client=discord.Client(intents=self.intent)
        self.tree = app_commands.CommandTree(self.client)
        self.readyDone = False

fromWhere = "main.py"
settingsCache = dict()
msgCache = OrderedDict()
susDict = dict()

bot = Asby()
client = bot.client
tree = bot.tree

if not os.environ.get("DATABASE_URL", ""):
    log(msg="No DATABASE_URL provided", evn=3, act=-1, fromWhere=fromWhere)
    sys.exit(1)


@client.event
async def on_ready():
    if not bot.readyDone :
        bot.readyDone = True
        if await asby.onReady.setup(client=client, tree=tree, cache=settingsCache):
            sys.exit(1)

@tasks.loop(minutes=5)
async def clear_msg_cache():
    await asby.msgCache.clear_msg_cahce(msgCache=msgCache, settingsCache=settingsCache)
    print(msgCache)
    
#---------------------------------
@has_permissions(administrator=True)
@tree.command(name="ping", description="Check the bot's latency")
async def ping(interaction: discord.Interaction):
    await asby.ping.ping(client=client,interaction=interaction)

#create spam channel
@has_permissions(administrator=True)
@app_commands.guild_only()
@app_commands.default_permissions(manage_channels=True)   # Discord hides it from non-admins
@app_commands.checks.bot_has_permissions(manage_channels=True)
@tree.command(name='csch',description="create a chat for trap a bot-spammer")
async def csch(interaction: discord.Interaction):
    await asby.csch.csch(interaction=interaction,cache=settingsCache)

#cancle the punishments
@has_permissions(administrator=True)
@app_commands.guild_only()
@app_commands.default_permissions(manage_channels=True)
@app_commands.checks.bot_has_permissions(administrator=True)
@app_commands.describe(
    user="Pick a user (only works for people still in the server)",
    userid="User ID (the number one, works for banned or kicked users)")
@tree.command(name='acquit',description="cancle the punishments, including timed out or ban")
async def acquit(interaction: discord.Interaction, user : discord.User | None = None, userid : str | None = None):
    if user :
       memberId = user.id
    else :
        try :
            memberId = int(userid)
        except :
            return await interaction.response.send_message("invalid userid (UID)",ephemeral=True)

    if not memberId:
        return await interaction.response.send_message(
            "you must provide user or user ID", ephemeral=True)
    await aq(interaction=interaction,userId=memberId, susDict=susDict)

#settings
@has_permissions(administrator=True)
@app_commands.guild_only()
@app_commands.default_permissions(manage_channels=True)
@tree.command(name='config',description="config bot parameters")
async def config(interaction: discord.Interaction):
    await interaction.response.send_message(
        "edit bot config", view=SettingsPanel(setting=settingsCache), ephemeral=True
    )
    print(settingsCache)


@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.BotMissingPermissions):
        msg = f"I'm missing permission(s): {', '.join(error.missing_permissions)}"
    else:
        name = interaction.command.name if interaction.command else "?"
        log(msg=f"/{name} failed: {error!r}", evn=3, act=1, fromWhere=fromWhere)
        msg = "Something went wrong. Please try again."

    if interaction.response.is_done():
        await interaction.followup.send(msg, ephemeral=True)
    else:
        await interaction.response.send_message(msg, ephemeral=True)


#---------------------------------
@client.event
async def on_guild_channel_delete(channel):
    await asby.delroom.delroom(guildId = channel.guild.id, chIds=channel.id, cache=settingsCache)

@client.event
async def on_message(message: discord.Message):
    # Ignore bots (including this one) and DMs (no guild -> no guild.id)
    if message.author.id == client.user.id:
        return

    susKey = (message.guild.id,message.author.id)
    if len(susDict.get(susKey,[])) >= settingsCache[message.guild.id]["minRooms"] :
        await message.delete()
        msg = """
        You have been flagged as a spam bot and every message you send will constantly get delete
        To remove this status, use the command /acquit on yourself.
        """
        await message.author.send(msg)
        return

    await asby.msgCache.update_msg_cache(msgCache=msgCache, settingsCache=settingsCache, msg=message)
    print(msgCache)
    await is_spam(message=message,settings=settingsCache,susDict=susDict,bot=client,msgCache=msgCache)


#===========================================================================
# run the bot
#===========================================================================

token = os.environ.get("BOT_TOKEN", "")
if not token:
    log(msg="No token provided", evn=3, act=-1, fromWhere=fromWhere)
    sys.exit(1)

try:
    client.run(token)
except Exception as e:
    log(msg=f"cannot start the bot, error :\n {e}", evn=3, act=-1, fromWhere=fromWhere)