from enum import member
import discord

from discord.ext import commands
import Imgs
import Msg

Botname = "Test Bot 001"    # Change this value to your bot name so the bot wont cought its self.
intent = discord.Intents.default()
intent.message_content = True
intent.members = True
client = commands.Bot(command_prefix="/", intents=intent)

UserMessageTable : dict[str,Msg.UserMessage] = {}
UserImageTable : dict[str,Imgs.UserFile] = {}

#--------------------------------- bot logic-------------------------------

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.content:
        print(message.author.name," : ",message.content)

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

    if message.attachments:
        if await Imgs.is_spam(
            str(message.author.name),
            int(message.guild.id),
            int(message.channel.id),
            message.attachments,
            UserImageTable
            ):
            await message.channel.send(f"Alert! user : {message.author.name} might be a spammer by sending image!")

    print(UserMessageTable)
    print(UserImageTable)
            
#===========================================================================
#run the bot
#===========================================================================

try:
    with open(file="token.txt",mode="r",encoding="UTF-8") as token:
        token = token.readline()
        client.run(token)
        
except FileNotFoundError :
    with open(file="token.txt",mode="w") as newTokenFile :
        token = str(input("Please enter your bots token : "))
        newTokenFile.write(token)

    with open(file="token.txt",mode="r",encoding="UTF-8") as token:
        token = token.readline()
        client.run(token)
except discord.LoginFailure :
    print("The bots token is invalid.")
except :
    print("Sorry, something went wrong. Please review the codes")