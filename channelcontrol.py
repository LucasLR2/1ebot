import discord
from discord.ext import commands
import asyncio

class ChannelControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bump_channel_id = 1392893710848622734  # ID real del canal de bumps
        self.allowed_commands = {"/bump", "!misbumps", "!clasificacion"}  # comandos visibles permitidos

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.channel.id == self.bump_channel_id:
            content = message.content.strip().lower()

            # Permitir si el autor tiene permisos de administrador y usa un comando (!...)
            if message.author.guild_permissions.administrator and content.startswith("!"):
                return  # se permite

            # Permitir comandos normales
            if content in self.allowed_commands:
                return

            # Si no está permitido, borrar y enviar aviso
            try:
                await message.delete()
            except discord.Forbidden:
                pass

            allowed_str = ", ".join(self.allowed_commands)
            alert = await message.channel.send(
                f"⚠️ Sólo se permiten los comandos:{allowed_str} en este canal."
            )
            await asyncio.sleep(10)
            try:
                await alert.delete()
            except discord.Forbidden:
                pass

# setup asíncrono
async def setup(bot):
    await bot.add_cog(ChannelControl(bot))
