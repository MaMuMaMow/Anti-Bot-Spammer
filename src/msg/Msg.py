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
    
def prob(message1:str,message2:str) -> bool :

    """
    This function will calculate a probability of the messages by using longest common subsequence.
    """

    if min(len(message1),len(message2)) < 20 or max(len(message1),len(message2)) > 5000 : # 20, 5e3 can be hyper parameters
        return False
    
    import subprocess
    try :
        maxNum = min(len(message1),len(message2))
        ans = subprocess.run(
            ["/app/src/exeFunc/LCS.exe"],
            input=f"{message1}'\n'{message2}",
            capture_output=True,
            text=True,
            check=True
        ).stdout

        if ( int(ans) >= int(maxNum*0.8) ) : # 0.8 can be hyper parameters
            return True
    
    except FileNotFoundError :
        print("Can't find the .exe file, please compile LCS.cpp first.")
    
    except Exception as e :
        print(f"Something went wrong with the .exe file. {e}")
        
    return False


def is_spam(username:str,server:int ,channal:int, message:str, UserMessageTable:dict) -> bool:

    """
    this function will first check if the message trend to be spam,
    if it might be a spam it will return True then update the value.
    else it will update and then return False.
    """

    try :
        Data  = UserMessageTable[username]
        same_server = Data.server == server
        not_same_channal = Data.channal != channal
        same_message = prob(Data.message,message)

        if (same_message and same_server and not_same_channal): #checking if it's spam
            UserMessageTable[username].update(server,channal,message)
            return True
        else :
            UserMessageTable[username].update(server,channal,message)

    except KeyError :
        UserMessageTable[username] = UserMessage(server,channal,message)

    except :
        print("Something went wrong, please review the code.")

    return False