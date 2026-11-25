import datetime
from datetime import timezone

def log(
        msg:str = "", 
        evn : int = -1, 
        act : int = -1, 
        fromWhere: str = "unknown"
        ):
    
    evnDict = {
       -1 : "[UNKNOWN]", 
        0 : "[START]",
        1 : "[INFO]",
        2 : "[WARN]",
        3 : "[ERR]",
    }
    
    actionDict = {
       -1 : "OTHER",
        0 : "COLLECT",
        1 : "COMMAND",
        2 : "ALERT",
        3 : "MUTE",
        4 : "KICK",
        5 : "BAN",
        6 : "DB",
    }

    now_utc = datetime.datetime.now(timezone.utc)
    logTime = now_utc.strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"{evnDict.get(evn,"[UNKNOWN]")} : {actionDict.get(act,"UNKNOWN")} | {fromWhere} {logTime}UTC: {msg}")