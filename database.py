import asyncpg
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()  # Cargar las variables del archivo .env si existe

DB_URL = os.getenv("DATABASE_URL")

async def connect():
    return await asyncpg.connect(DB_URL)

async def setup():
    conn = await connect()

    # Crear tabla bumps
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS bumps (
            user_id TEXT NOT NULL,
            guild_id TEXT NOT NULL,
            count INT DEFAULT 1,
            PRIMARY KEY (user_id, guild_id)
        );
    ''')

    # Crear tabla euros (economía)
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS euros (
            user_id TEXT NOT NULL,
            guild_id TEXT NOT NULL,
            balance FLOAT DEFAULT 0,
            PRIMARY KEY (user_id, guild_id)
        );
    ''')

    # Crear tabla tienda (tienda)
    await conn.execute('''
        CREATE TABLE tienda (
        id SERIAL PRIMARY KEY,
        nombre TEXT NOT NULL UNIQUE,
        precio INTEGER NOT NULL CHECK (precio >= 0)
    );
    ''')

    # Crear tabla inventario (inventario de usuarios)
    await conn.execute('''
        CREATE TABLE inventario (
        id SERIAL PRIMARY KEY,
        usuario_id BIGINT NOT NULL,
        objeto_id INTEGER NOT NULL REFERENCES tienda(id) ON DELETE CASCADE,
        cantidad INTEGER NOT NULL DEFAULT 1 CHECK (cantidad > 0)
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

# Ejecutar setup si se llama directamente este script
if __name__ == "__main__":
    asyncio.run(setup())
