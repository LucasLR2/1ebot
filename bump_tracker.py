import discord
from discord.ext import commands
import os, asyncio
from datetime import datetime, timezone
from database import add_bump, get_bumps, get_all_bumps

DISBOARD_BOT_ID  = 302050872383242240
ROLE_ID_TO_PING  = 1392903420020658196
CHANNEL_ID       = 1392893710848622734
COUNTDOWN        = 2 * 60 * 60  # 2 horas
EMBED_COLOR      = 0x00ffff

class BumpTracker(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tasks: dict[int, asyncio.Task] = {}
        self.pending_bumps: dict[int, int] = {}  # user_id que ejecutó el bump

    # ───────────── listener para TODOS los mensajes del canal ─────────────
    @commands.Cog.listener("on_message")
    async def monitor_all_messages(self, message: discord.Message):
        if message.channel.id != CHANNEL_ID:
            return

        if message.author.id == DISBOARD_BOT_ID:
            await self.disboard_only_bump(message)
            return

        if message.content.strip().lower() == "/bump":
            self.pending_bumps[message.guild.id] = message.author.id

    # ───────────── procesamiento de mensajes de DISBOARD ─────────────
    async def disboard_only_bump(self, message: discord.Message):
        if message.interaction:
            cmd = (message.interaction.name or "").lower()
            user_id = message.interaction.user.id

            if cmd != "bump":
                try:
                    await message.delete()
                except discord.Forbidden:
                    pass
                return

            self.pending_bumps[message.guild.id] = user_id

            if not (message.content or message.embeds):
                return

        if not message.embeds:
            return

        embed = message.embeds[0]
        text  = f"{embed.title or ''} {embed.description or ''}".lower()

        is_success = "bump done" in text or "¡hecho!" in text
        if not is_success:
            try:
                await message.delete()
            except discord.Forbidden:
                pass
            return

        guild_id = message.guild.id
        if guild_id not in self.pending_bumps:
            return

        user_id = self.pending_bumps.pop(guild_id)

        # ── Agradecimiento y contador (DB) ──
        total = await add_bump(user_id, guild_id)

        thanks = discord.Embed(
            description=(
                "🙌 **¡Mil gracias!**\n"
                f"💖 Agradecemos que hayas bumpeado nuestro servidor, <@{user_id}>.\n"
                f"🌟 Has realizado **{total}** bumps en total. ¡Fantástico!"
            ),
            color=EMBED_COLOR,
            timestamp=datetime.now(timezone.utc)
        )
        await message.channel.send(embed=thanks)

        if task := self.tasks.get(guild_id):
            task.cancel()
        self.tasks[guild_id] = self.bot.loop.create_task(self._recordatorio(message.channel))

    async def _recordatorio(self, channel: discord.TextChannel):
        try:
            await asyncio.sleep(COUNTDOWN)
        except asyncio.CancelledError:
            return

        role = channel.guild.get_role(ROLE_ID_TO_PING)
        mention = role.mention if role else "@here"

        embed = discord.Embed(
            description=(
                "🕒 **¡Es momento de hacer un bump!**\n"
                "Utiliza **/bump** para apoyar al servidor.\n\n"
                "*1€ BRAWL PASS PLUS • Sistema de recordatorio de bump*"
            ),
            color=EMBED_COLOR,
            timestamp=datetime.now(timezone.utc)
        )
        await channel.send(content=mention, embed=embed)

    @commands.command(name="clasificacion")
    async def clasificacion(self, ctx):
        """Muestra el ranking de usuarios por cantidad de bumps"""
        bumps = await get_all_bumps(ctx.guild.id)
        if not bumps:
            await ctx.send("❌ No hay bumps registrados aún.")
            return

        top = "\n".join(
            f"**{i+1}.** <@{uid}> — **{count}** bumps"
            for i, (uid, count) in enumerate(bumps[:10])
        )

        embed = discord.Embed(
            title="🏆 Clasificación de Bumps",
            description=top,
            color=EMBED_COLOR
        )
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        print("[BumpTracker] Módulo de bumps listo")

async def setup(bot: commands.Bot):
    await bot.add_cog(BumpTracker(bot))
