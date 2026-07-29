import hashlib
from pathlib import Path

class UserFile :
    def __init__(self, server:int = "", channal:int = "", image:list = ""):
        self.server = int(server)
        self.channal = int(channal)
        self.image = [[None for _ in range(10)] for _ in range(int(1e4))]

    
    def update(self, server:str, channal:str, image:list):
        self.server = int(server)
        self.channal = int(channal)
        for i in range(0,len(image),1):
            self.image[i] = image[i]

    def add(self,image:list):
        self.image.append(image)

    def get_value(self) -> tuple:
        return (self.server, self.channal, self.image)

    
def is_spam(self, OldImage:UserFile, NewImage:UserFile) -> bool :
    ServerCondition = OldImage.server == NewImage.server
    ChannelCondition = OldImage.channal != NewImage.channal
    ImageCondition = 0



        
    return 0