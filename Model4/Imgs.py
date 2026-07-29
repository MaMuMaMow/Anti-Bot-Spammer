class UserFile :
    def __init__(self, server:int = 0, channal:int = 0, hashed_image_set:set = None):
        self.server = int(server)
        self.channal = int(channal)
        self.image = hashed_image_set if hashed_image_set is not None else set()
        
    def update(self, server:int = 0, channel:int = 0, hashed_image_set:set = None):
        self.server = server
        self.channal = channel
        self.image = hashed_image_set if hashed_image_set is not None else set()
        

async def make_new_UserFile(Files:list) -> set:
    from PIL import Image
    import imagehash
    import io

    currentImg = set()
    for attachment in Files :
        if attachment.content_type and attachment.content_type.startswith('image/'):
            img = await attachment.read()
            currentImg.add(imagehash.phash(Image.open(io.BytesIO(img))))

    return currentImg

async def is_spam(username:str, server:int ,channal:int ,Files:list, UserImageTable:dict) -> bool:
    """
    This function will check if the new set of pictures similar with the old one.
    If yes, it will return True without update, else it will return False and update new set.
    """
    currentImg = await make_new_UserFile(Files)
    if len(currentImg) == 0:
            return False
    
    try:
        ServerCondition = server == UserImageTable[username].server
        ChannalCondition = channal != UserImageTable[username].channal
        if (not (ServerCondition and ChannalCondition)):
            return False

        OldImg = UserImageTable[username].image
        MaxPercent = len(OldImg)
        count = 0
        for img in currentImg :
            if img in OldImg :
                count+=1
        if count > MaxPercent*0.8: #can be hyper parameter
            return True
        
    except KeyError:
            UserImageTable[username] = UserFile(server,channal,currentImg)
            return False

    UserImageTable[username].update(server,channal,currentImg)
    return False