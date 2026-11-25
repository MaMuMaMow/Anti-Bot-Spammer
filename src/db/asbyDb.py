"""
All database code lives here. The rest of the bot only calls these functions
and never writes SQL itself, so the database can be swapped later if needed.

Note: Postgres folds unquoted names to lowercase, so the column "minRooms" is
really "minrooms" in the DB. Rows are converted back to the camelCase names
below before they leave this file, so the rest of the bot only sees camelCase.
"""
import asyncpg
from logger.logger import log
from db import onReady

fromWhere = "/db/asbyDb.py"


# ----------------------------- connection ---------------------------------
def db() -> asyncpg.Pool:
    if onReady.pool is None:
        raise RuntimeError("/db/onReady.py/init() has not been called")
    return onReady.pool


# ----------------------------- settings fields ----------------------------
MAX_ROOMS = 10
PUNISHMENTS = ("ban", "kick", "timeout")
MAX_TIMEOUT = 28 * 24 * 60 * 60     # Discord's limit: 28 days, in seconds

# every setting column (see README "settings" + "advance settings")
SETTINGS_KEYS = (
    "punishment",          # /   ban / kick / timeout
    "timeoutDuration",     # /   second, used when punishment is timeout (max 28 days)
    "msgCacheDelAmount",   #     max 50
    "msgCacheDelTime",     #     max 1800 second
    "minRooms",            # /   minimum spam rooms a user must post in
    "msgCacheDuration",    # /   max 1800 second
    "msgCacheAmount",      # /   max 50
    "timeGap",             #     max 3600
)

# keys update_setting() accepts besides guildId
UPDATABLE_KEYS = ("chIds",) + SETTINGS_KEYS

# integer settings: (min, max)
INT_LIMITS = {
    "minRooms":           (1, MAX_ROOMS),
    "timeoutDuration":    (60, MAX_TIMEOUT),
    "msgCacheDelAmount":  (1, 50),
    "msgCacheDelTime":    (1, 1800),
    "msgCacheDuration": (1, 1800),
    "msgCacheAmount":   (1, 50),
    "timeGap":   (1, 3600),
}

# column list used in every SELECT / RETURNING
COLUMNS = ", ".join(("guildId",) + UPDATABLE_KEYS)


def is_int(value) -> bool:
    # bool is a subclass of int in Python (True == 1), so reject it explicitly
    return isinstance(value, int) and not isinstance(value, bool)


def validate(key: str, value):
    """Check one setting and return the value to store. Raises ValueError."""
    if key in INT_LIMITS:
        lo, hi = INT_LIMITS[key]
        if not is_int(value) or not lo <= value <= hi:
            raise ValueError(f"{key} must be an integer between {lo} and {hi}")
        return value

    if key == "punishment":
        if value not in PUNISHMENTS:
            raise ValueError(f"punishment must be one of {PUNISHMENTS}")
        return value

    if key == "chIds":
        if isinstance(value, (str, bytes)) or not hasattr(value, "__iter__"):
            raise ValueError("chIds must be a list/set of channel ids")
        ids = set(value)
        if not all(is_int(c) and c > 0 for c in ids):
            raise ValueError("chIds must contain only channel ids")
        if len(ids) > MAX_ROOMS:
            raise ValueError(f"chIds can hold at most {MAX_ROOMS} rooms")
        return sorted(ids)          # asyncpg wants a list for BIGINT[]


    if key == "timeGap":
        if not isinstance(value, int) :
            raise ValueError("timeGap must be int")
        if  not (INT_LIMITS[key][0] <= value <= INT_LIMITS[key][1])  :
            raise ValueError(f"timeGap must be between {INT_LIMITS[key][0]} and {[key][1]}")
        return value
    
    raise ValueError(f"unknown setting: {key}")


def row_to_settings(row) -> dict:
    """DB row (lowercase keys) -> cache entry (camelCase keys, chIds as a set)."""
    settings = {key: row[key.lower()] for key in SETTINGS_KEYS}
    settings["chIds"] = set(row["chids"])
    return settings


# ----------------------------- spmRoomSettings ----------------------------

async def add_chId(guildId: int, chIds: int, minRooms: int = 1) -> None:
    """
    Add ONE channel id to a guild (the parameter is still called chIds so
    existing calls keep working). minRooms is only used when the guild is new;
    an existing guild keeps its own minRooms. Adding the same id twice is a no-op.
    """
    await db().execute(
        """
        INSERT INTO spmRoomSettings (guildId, chIds, minRooms)
        VALUES ($1, ARRAY[$2::BIGINT], $3)
        ON CONFLICT (guildId) DO UPDATE
        SET chIds = CASE
            WHEN $2::BIGINT = ANY(spmRoomSettings.chIds) THEN spmRoomSettings.chIds
            ELSE array_append(spmRoomSettings.chIds, $2::BIGINT)
        END
        """,
        guildId, chIds, minRooms
    )


async def get_spam_room(guildId: int) -> dict | None:
    """One guild's settings (same shape as a cache entry), or None if not found."""
    row = await db().fetchrow(
        f"SELECT {COLUMNS} FROM spmRoomSettings WHERE guildId = $1", guildId
    )
    return row_to_settings(row) if row else None


async def set_chIds(guildId: int, alive: list) -> None:
    await db().execute(
        "UPDATE spmRoomSettings SET chIds = $2::BIGINT[] WHERE guildId = $1",
        guildId, alive
    )


async def get_all_spam_rooms() -> dict[int, dict]:
    """
    {
        guildId: {
            "chIds": {chId, ...},
            "minRooms": int,
            "punishment": str,
            ... every key in SETTINGS_KEYS
        }
    }
    for every server - used to fill the in-memory cache.
    """
    rows = await db().fetch(f"SELECT {COLUMNS} FROM spmRoomSettings")
    return {r["guildid"]: row_to_settings(r) for r in rows}

#dict is the settingsCache
async def update_setting(data: dict) -> dict:
    """
    Insert or update one guild's settings when a user configures them.

    data must contain "guildId", plus any of: chIds, punishment,
    timeoutDuration, msgCacheDelAmount, msgCacheDelTime, wantLog, logChId, minRooms,
    msgCacheDuration, msgCacheAmount.

    Only the keys present in `data` are changed. Everything else keeps its
    current value (or the column default if the guild is new).

        await update_setting({"guildId": 123, "punishment": "kick", "wantLog": True})

    Note: "chIds" REPLACES the whole list. To add/remove one room use
    add_chId() / remove_chId() instead.

    Returns the guild's full settings after the update, in the same shape as a
    cache entry, so the caller can do:
        cache[guildId] = await update_setting(data)

    Raises ValueError if guildId is missing, a key is unknown, or a value is
    invalid. Nothing is written in that case.
    """
    data = dict(data)                       # don't modify the caller's dict
    guildId = data.pop("guildId", None)
    if not is_int(guildId):
        raise ValueError("guildId (int) is required")

    unknown = set(data) - set(UPDATABLE_KEYS)
    if unknown:
        raise ValueError(f"unknown setting(s): {sorted(unknown)}")

    values = {key: validate(key, value) for key, value in data.items()}

    # Column names can't be $-parameters, so they go into the SQL text.
    # That's safe here: every name was checked against UPDATABLE_KEYS above.
    cols = list(values)
    placeholders = ", ".join(f"${i}" for i in range(1, len(cols) + 2))
    if cols:
        setPart = ", ".join(f"{c} = EXCLUDED.{c}" for c in cols)
    else:
        setPart = "guildId = EXCLUDED.guildId"   # nothing to change; still return the row

    row = await db().fetchrow(
        f"""
        INSERT INTO spmRoomSettings ({", ".join(["guildId", *cols])})
        VALUES ({placeholders})
        ON CONFLICT (guildId) DO UPDATE SET {setPart}
        RETURNING {COLUMNS}
        """,
        guildId, *values.values()
    )

    log(msg=f"updated settings for guild {guildId}: {', '.join(cols) or 'nothing'}",
        evn=1, act=6, fromWhere=f"{fromWhere}/update_setting()")
    return row_to_settings(row)


async def delete_guild(guild_id: int) -> None:
    await db().execute("DELETE FROM spmRoomSettings WHERE guildId = $1", guild_id)


async def remove_chId(guildId: int, chId: int) -> None:
    await db().execute(
        """
        UPDATE spmRoomSettings
        SET chIds = array_remove(chIds, $2::BIGINT)
        WHERE guildId = $1
        """,
        guildId, chId,
    )