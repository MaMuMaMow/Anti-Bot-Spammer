from enum import member
import discord

Botname = "Test Bot 001"    # Change this value to your bot name so the bot wont cought its self.
intent = discord.Intents.default()
intent.message_content = True
intent.members = True
client = discord.Client(intents=intent)

class UserMessage :
    def __init__(self, server:int = "", channal:int = "", message:str = ""):
        self.server = int(server)
        self.channal = int(channal)
        self.message = str(message)
    
    def update(self, server:str, channal:str, message:str):
        self.server = int(server)
        self.channal = int(channal)
        self.message = str(message)

    def get_value(self) -> tuple:
        return (self.server, self.channal, self.message)

UserMessageTable :dict[str,UserMessage]= {}

#================================================================================================

def is_spam(username:str,server:int ,channal:int, message:str) -> bool:

    """
    this function will first check if the message trend to be spam,
    if it might be a spam it will update value then update
    else it will update and then return False
    """

    try :
        Data  = UserMessageTable[username].get_value()
        #print(Data)
        same_server = Data[0] == server
        not_same_channal = Data[1] != channal
        same_message = Data[2] == message
        #print(same_message,same_server,not_same_channal,"<-")

        if (same_message and same_server and not_same_channal): #checking if it's spam
            UserMessageTable[username].update(server,channal,message)
            return True
        else :
            UserMessageTable[username].update(server,channal,message)

    except KeyError :
        UserMessageTable[username] = UserMessage(server,channal,message)

    return False

#--------------------------------- bot logic-------------------------------

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    print(message.author.name,client.get_user,message.content)

    
    if (str(message.author.name) != Botname) :

        print("current data :",message.author.name,message.guild.id ,message.channel.id ,message.content)
        if is_spam(str(message.author.name),int(message.guild.id) ,int(message.channel.id) ,str(message.content)):
            await message.channel.send(f"Alert! user : {message.author.name} might be a spammer!")

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