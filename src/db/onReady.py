import asyncpg
from logger.logger import log
pool: asyncpg.Pool | None = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS spmRoomSettings (
    guildId BIGINT PRIMARY KEY,
    chIds BIGINT[] NOT NULL DEFAULT '{}',
    minRooms INTEGER NOT NULL DEFAULT 1
);

ALTER TABLE spmRoomSettings
    ADD COLUMN IF NOT EXISTS punishment TEXT NOT NULL DEFAULT 'timeout'
        CHECK (punishment IN ('ban', 'kick', 'timeout')),
    ADD COLUMN IF NOT EXISTS timeoutDuration INTEGER NOT NULL DEFAULT 3600
        CHECK (timeoutDuration BETWEEN 60 AND 2419200),
    ADD COLUMN IF NOT EXISTS msgCacheDelAmount INTEGER NOT NULL DEFAULT 20
        CHECK (msgCacheDelAmount BETWEEN 1 AND 50),
    ADD COLUMN IF NOT EXISTS msgCacheDelTime INTEGER NOT NULL DEFAULT 600
        CHECK (msgCacheDelTime BETWEEN 1 AND 1800),
    ADD COLUMN IF NOT EXISTS msgCacheDuration INTEGER NOT NULL DEFAULT 600
        CHECK (msgCacheDuration BETWEEN 1 AND 1800),
    ADD COLUMN IF NOT EXISTS msgCacheAmount INTEGER NOT NULL DEFAULT 20
        CHECK (msgCacheAmount BETWEEN 1 AND 50),
    ADD COLUMN IF NOT EXISTS timeGap INTEGER NOT NULL DEFAULT 5
        CHECK (timeGap BETWEEN 1 AND 3600),
    ADD COLUMN IF NOT EXISTS initMsg BOOLEAN NOT NULL DEFAULT TRUE
"""

async def init(dsn: str) -> None:
    """Open a connection pool and make sure the tables exist."""
    fromWhere = "/db/onReady.py/init()"
    global pool
    if pool is not None:
        return
    pool = await asyncpg.create_pool(dsn, min_size=1, max_size=5)
    async with pool.acquire() as conn:
        await conn.execute(SCHEMA)
    log(msg="Database connected, schema ready", evn=1,act=6, fromWhere=fromWhere)

async def close() -> None:
    global pool
    if pool is not None:
        await pool.close()
        pool = None