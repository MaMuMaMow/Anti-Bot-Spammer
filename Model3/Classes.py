import hashlib
from pathlib import Path

class UserFile :
    def __init__(self, server:int = 0, channal:int = 0, hashed_image_set:set = set()):
        self.server = int(server)
        self.channal = int(channal)
        self.image = set()
        for hashed_image in hashed_image_set :
            self.image.add(hashed_image)
        
    def update(self, server:int = 0, channel:int = 0, hashed_image_set:set = set()):
        self.server = server
        self.channal = channel
        self.image.clear()
        for hashed_image in hashed_image_set :
            self.image.add(hashed_image)

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

def is_spam(OldImg:set,NewImg:set) -> bool:
    MaxPercent = len(OldImg)
    count = 0
    for img in NewImg :
        if img in OldImg :
            count+=1

    if count > MaxPercent*0.8:
        return 1

    return 0