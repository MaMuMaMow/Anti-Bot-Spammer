Since the project owner is still in internship, he has no proper time for writing a handbooks.

So if possible, please learing how the bot works by yourself. Thank you for understanding.

1) docker build :
```bash
docker build -f ./Dockerfile -t anti-spammer:1.0 .
```

2) run :
```bash
docker compose up --build
```

3) stop bot :
```bash
docker compose down
```

3) clear database :
```bash
docker compose down -v
```
---

## settings :
| name | note | db field |
|---|---|---|
| punishment | ban/ kick/ timeout | punishment (string )|
| timeoutDuration | second | timeoutDuration (int) |
| message delete amount | max 50 | msgCacheDelAmount (int) |
| time gap for each message | max 50 | timeGap (int) |
| message delete time | max 1800 second | msgCacheDelTime (int) |
| min spam room | minimum of send msg spam room | minRooms (int) |
| init message | let the bot sent message when create spam room | initMsg (bool)

---

## advance settings
| name | note | db field |
|---|---|---|
| message caching duration | max 1800 second | msgCachingDuration (int) |
| message caching amount | max 50 | msgCachingAmount (int) |