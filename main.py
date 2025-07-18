import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
from database import setup, connect  # ← Asegúrate de importar también `connect`

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def test(ctx):
    await ctx.send("¡Hola! Estoy funcionando correctamente.")

@bot.event
async def on_ready():
    print(f"Estoy en línea como {bot.user.name} (ID: {bot.user.id})")

async def main():
    async with bot:
        await setup()
        bot.db = await connect()  # ✅ Conexión global para usar en cogs como `self.bot.db`

        await bot.load_extension("admin_commands")
        await bot.load_extension("bump_tracker")
        await bot.load_extension("channelcontrol")
        await bot.load_extension("usercommands")
        await bot.load_extension("embed_commands")
        await bot.load_extension("economia")

        await bot.start(os.getenv('TOKEN'))

asyncio.run(main())