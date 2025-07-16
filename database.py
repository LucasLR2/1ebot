import asyncpg
import aiosqlite
import os

DB_URL = os.getenv("DATABASE_URL")

async def connect():
    return await asyncpg.connect(DB_URL)

async def setup():
    conn = await connect()
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS bumps (
            user_id TEXT NOT NULL,
            guild_id TEXT NOT NULL,
            count INT DEFAULT 1,
            PRIMARY KEY (user_id, guild_id)
        );
    ''')
    await conn.close()

async def add_bump(user_id: int, guild_id: int) -> int:
    conn = await connect()
    await conn.execute('''
        INSERT INTO bumps (user_id, guild_id, count)
        VALUES ($1, $2, 1)
        ON CONFLICT (user_id, guild_id)
        DO UPDATE SET count = bumps.count + 1;
    ''', str(user_id), str(guild_id))

    result = await conn.fetchval('''
        SELECT count FROM bumps
        WHERE user_id = $1 AND guild_id = $2;
    ''', str(user_id), str(guild_id))

    await conn.close()
    return result or 0

async def get_bumps(user_id, guild_id):
    conn = await connect()
    result = await conn.fetchval('''
        SELECT count FROM bumps WHERE user_id = $1 AND guild_id = $2;
    ''', str(user_id), str(guild_id))
    await conn.close()
    return result or 0

async def get_all_bumps(guild_id):
    conn = await connect()
    rows = await conn.fetch('''
        SELECT user_id, count
        FROM bumps
        WHERE guild_id = $1
        ORDER BY count DESC;
    ''', str(guild_id))
    await conn.close()
    return [(row['user_id'], row['count']) for row in rows]