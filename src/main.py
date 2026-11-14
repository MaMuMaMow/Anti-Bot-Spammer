from enum import member
import discord
import os
import sys

from discord.ext import commands
from img import Imgs
from msg import Msg
from logger.logger import log

Botname = "Test Bot 001"    # Change this value to your bot name so the bot wont cought its self.
intent = discord.Intents.default()
intent.message_content = True
intent.members = True
client = commands.Bot(command_prefix="/", intents=intent)

UserMessageTable : dict[str,Msg.UserMessage] = {}
UserImageTable : dict[str,Imgs.UserFile] = {}

fromWhere = "main.py"

#--------------------------------- bot logic-------------------------------

@client.event
async def on_ready():
    log(msg='We have logged in as {0.user}'.format(client), evn=0,fromWhere=fromWhere)

@client.event
async def on_message(message):
    if message.content:
        log(msg=f'{message.author.name}" : {message.content}',evn=1,act=0,fromWhere=fromWhere)

        msg = message.content.replace("\n","")
        msg = msg.replace(" ","")

        if (str(message.author.name) != Botname) :
            try:
                if Msg.is_spam(
                    str(message.author.name),
                    int(message.guild.id),
                    int(message.channel.id),
                    str(msg) ,UserMessageTable
                    ):
                    await message.channel.send(f"Alert! user : {message.author.name} might be a spammer!")
            except KeyError:
                UserMessageTable[message.author.name] = Msg.UserMessage(message.guild.id,message.channal.id,message.content)

    if message.attachments and await Imgs.is_spam(
            str(message.author.name),
            int(message.guild.id),
            int(message.channel.id),
            message.attachments,
            UserImageTable
            ):
            await message.channel.send(f"Alert! user : {message.author.name} might be a spammer by sending image!")
            
#===========================================================================
#run the bot
#===========================================================================

token = os.environ.get("BOT_TOKEN","")
if not token :
    log(msg="No token provided",evn=3,act=-1,fromWhere=fromWhere)
    sys.exit(1)
        
try :
    client.run(token)
except Exception as e:
    log(msg=f"cannot start the bot, error :\n {token}",evn=3,act=-1,fromWhere=fromWhere)