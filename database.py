import asyncpg
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

async def connect():
    return await asyncpg.connect(DB_URL)

async def setup():
    conn = await connect()

    # Tabla de bumps
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS bumps (
            user_id TEXT NOT NULL,
            guild_id TEXT NOT NULL,
            count INT DEFAULT 1,
            PRIMARY KEY (user_id, guild_id)
        );
    ''')

    # Tabla de euros
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS euros (
            user_id TEXT NOT NULL,
            guild_id TEXT NOT NULL,
            balance FLOAT DEFAULT 0,
            PRIMARY KEY (user_id, guild_id)
        );
    ''')

    # Tabla de tienda
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS tienda (
            id SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL UNIQUE,
            precio INTEGER NOT NULL CHECK (precio >= 0)
        );
    ''')

    # Tabla de inventario
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS inventario (
            id SERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            guild_id TEXT NOT NULL,
            objeto_id INTEGER NOT NULL REFERENCES tienda(id) ON DELETE CASCADE,
            cantidad INTEGER NOT NULL DEFAULT 1 CHECK (cantidad > 0)
        );
    ''')

    await conn.close()

# Funciones de bumps
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

# Función para agregar euros
async def add_euros(user_id, guild_id, amount):
    conn = await connect()
    await conn.execute('''
        INSERT INTO euros (user_id, guild_id, balance)
        VALUES ($1, $2, $3)
        ON CONFLICT (user_id, guild_id)
        DO UPDATE SET balance = euros.balance + $3;
    ''', str(user_id), str(guild_id), amount)
    await conn.close()

# Función para obtener balance
async def get_balance(user_id, guild_id):
    conn = await connect()
    balance = await conn.fetchval('''
        SELECT balance FROM euros
        WHERE user_id = $1 AND guild_id = $2;
    ''', str(user_id), str(guild_id))
    await conn.close()
    return balance or 0

# Función para ver tienda
async def get_tienda():
    conn = await connect()
    rows = await conn.fetch('SELECT id, nombre, precio FROM tienda ORDER BY id')
    await conn.close()
    return rows

# Función para comprar
async def comprar_objeto(user_id, guild_id, objeto_id):
    conn = await connect()

    # Obtener precio del objeto
    objeto = await conn.fetchrow('SELECT precio FROM tienda WHERE id = $1', objeto_id)
    if not objeto:
        await conn.close()
        return "❌ Objeto no encontrado."

    precio = objeto["precio"]

    # Verificar saldo
    balance = await conn.fetchval('''
        SELECT balance FROM euros WHERE user_id = $1 AND guild_id = $2;
    ''', str(user_id), str(guild_id))

    if balance is None or balance < precio:
        await conn.close()
        return "💸 No tienes suficientes euros."

    # Restar euros
    await conn.execute('''
        UPDATE euros
        SET balance = balance - $1
        WHERE user_id = $2 AND guild_id = $3;
    ''', precio, str(user_id), str(guild_id))

    # Insertar objeto al inventario o sumar cantidad
    await conn.execute('''
        INSERT INTO inventario (user_id, guild_id, objeto_id, cantidad)
        VALUES ($1, $2, $3, 1)
        ON CONFLICT (user_id, guild_id, objeto_id)
        DO UPDATE SET cantidad = inventario.cantidad + 1;
    ''', str(user_id), str(guild_id), objeto_id)

    await conn.close()
    return f"✅ Has comprado el objeto con ID {objeto_id} por {precio}€."

# Ejecutar setup
if __name__ == "__main__":
    asyncio.run(setup())
