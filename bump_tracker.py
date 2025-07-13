# bump_tracker.py
import discord
from discord.ext import commands
import json, os, asyncio
from datetime import datetime, timezone

DISBOARD_BOT_ID  = 302050872383242240
ROLE_ID_TO_PING  = 1392903420020658196
CHANNEL_ID       = 1392893710848622734
DATA_FILE        = "bump_data.json"
COUNTDOWN        = 2 * 60 * 60  # 2 horas
EMBED_COLOR      = 0x00ffff

class BumpTracker(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bump_data: dict[str, int] = self._load_data()
        self.tasks: dict[int, asyncio.Task] = {}
        self.pending_bumps: dict[int, int] = {}  # user_id que ejecutó el bump

    # ──────────── utilidades de almacenamiento ────────────
    def _load_data(self):
        if os.path.isfile(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.bump_data, f, indent=4)

    def _add_bump(self, uid: int) -> int:
        s = str(uid)
        self.bump_data[s] = self.bump_data.get(s, 0) + 1
        self._save_data()
        return self.bump_data[s]

    # ───────────── listener para TODOS los mensajes del canal ─────────────
    @commands.Cog.listener("on_message")
    async def monitor_all_messages(self, message: discord.Message):
        # Solo monitorear el canal específico
        if message.channel.id != CHANNEL_ID:
            return
            
        print(f"[DEBUG] Mensaje en canal: autor={message.author.id}, contenido='{message.content}', embeds={len(message.embeds)}")
        
        # Si es de DISBOARD, procesar
        if message.author.id == DISBOARD_BOT_ID:
            await self.disboard_only_bump(message)
            return
            
        # Si alguien escribe "/bump" manualmente (por si acaso)
        if message.content.strip().lower() == "/bump":
            self.pending_bumps[message.guild.id] = message.author.id
            print(f"[DEBUG] Bump pendiente agregado por mensaje manual: user_id={message.author.id}")

    # ───────────── procesamiento de mensajes de DISBOARD ─────────────
    async def disboard_only_bump(self, message: discord.Message):
        if message.channel.id != CHANNEL_ID or message.author.id != DISBOARD_BOT_ID:
            return

        print(f"[DEBUG] Mensaje de DISBOARD detectado")
        print(f"[DEBUG] Contenido: '{message.content}'")
        print(f"[DEBUG] Tiene interaction: {message.interaction is not None}")
    # ───────────── procesamiento de mensajes de DISBOARD ─────────────
    async def disboard_only_bump(self, message: discord.Message):
        print(f"[DEBUG] Procesando mensaje de DISBOARD")
        print(f"[DEBUG] Contenido: '{message.content}'")
        print(f"[DEBUG] Tiene interaction: {message.interaction is not None}")
        if message.embeds:
            print(f"[DEBUG] Embeds encontrados: {len(message.embeds)}")
            for i, embed in enumerate(message.embeds):
                print(f"[DEBUG] Embed {i}: title='{embed.title}', description='{embed.description}'")

        # 1) Si el mensaje proviene de un slash‑command de DISBOARD…
        if message.interaction:
            cmd = (message.interaction.name or "").lower()
            user_id = message.interaction.user.id
            print(f"[DEBUG] Comando slash detectado: '{cmd}' por usuario {user_id}")
            
            # • Si NO es /bump → bórralo y sal.
            if cmd != "bump":
                try:
                    await message.delete()
                except discord.Forbidden:
                    print("[BumpTracker] No tengo permisos para borrar mensajes.")
                return
            
            # Si es /bump, guardamos quién lo ejecutó
            self.pending_bumps[message.guild.id] = user_id
            print(f"[DEBUG] Bump pendiente agregado: user_id={user_id}, guild_id={message.guild.id}")
            
            # Si el mensaje tiene contenido (respuesta visible), procesamos
            if message.content or message.embeds:
                print("[DEBUG] Mensaje visible de /bump, continuando procesamiento...")
                # Continúa al procesamiento de embeds más abajo
            else:
                print("[DEBUG] Mensaje sin contenido (posiblemente efímero), esperando confirmación...")
                return  # Esperamos la confirmación como embed separado

        # 2) Si llega un embed (respuesta pública)
        if not message.embeds:
            print("[DEBUG] No hay embeds, saliendo...")
            return
            
        embed = message.embeds[0]
        text  = f"{embed.title or ''} {embed.description or ''}".lower()
        print(f"[DEBUG] Texto del embed: '{text}'")

        # Verificar si es un bump exitoso
        is_success = "bump done" in text or "¡hecho!" in text
        print(f"[DEBUG] ¿Es bump exitoso? {is_success}")

        # • Si no es un bump exitoso → bórralo (otro comando o bump fallido)
        if not is_success:
            print("[DEBUG] No es un bump exitoso, borrando mensaje...")
            try:
                await message.delete()
            except discord.Forbidden:
                pass
            return

        # • Verificar que hay un bump pendiente para este servidor
        guild_id = message.guild.id
        print(f"[DEBUG] Bumps pendientes: {self.pending_bumps}")
        if guild_id not in self.pending_bumps:
            print(f"[DEBUG] No hay bump pendiente para guild_id={guild_id}")
            return
        
        # • Obtener el usuario que ejecutó el bump
        user_id = self.pending_bumps.pop(guild_id)  # Remover del pending
        print(f"[DEBUG] Procesando bump exitoso para user_id={user_id}")

        # ── Agradecimiento y contador (SOLO si el bump fue aprobado) ──
        total = self._add_bump(user_id)
        thanks = discord.Embed(
            description=(
                "🙌 **¡Mil gracias!**\n"
                f"💖 Agradecemos que hayas bumpeado nuestro servidor, <@{user_id}>.\n"
                f"🏆 Has realizado **{total}** bumps en total. ¡Fantástico!"
            ),
            color=EMBED_COLOR,
            timestamp=datetime.now(timezone.utc)
        )
        await message.channel.send(embed=thanks)

        # Reinicia contador para recordatorio (SOLO tras bump aprobado)
        if task := self.tasks.get(guild_id):
            task.cancel()
        self.tasks[guild_id] = self.bot.loop.create_task(self._recordatorio(message.channel))

    # ───────── recordatorio tras COUNTDOWN ─────────
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

    @commands.command(name="fake_bump")
    @commands.has_permissions(administrator=True)
    async def fake_bump_command(self, ctx, user: discord.Member = None):
        """Simula que un usuario ejecutó /bump (para testing)"""
        if user is None:
            user = ctx.author
        
        self.pending_bumps[ctx.guild.id] = user.id
        await ctx.send(f"✅ Simulado: {user.mention} ejecutó `/bump`. Ahora cuando DISBOARD confirme un bump exitoso, se activará el sistema.")

    @commands.command(name="clear_pending")
    @commands.has_permissions(administrator=True)
    async def clear_pending_bumps(self, ctx):
        """Limpia todos los bumps pendientes"""
        count = len(self.pending_bumps)
        self.pending_bumps.clear()
        await ctx.send(f"✅ Se limpiaron {count} bumps pendientes.")

    # ───────── comando de prueba (REMOVER EN PRODUCCIÓN) ─────────
    @commands.command(name="test_bump")
    @commands.has_permissions(administrator=True)
    async def test_bump_flow(self, ctx, user: discord.Member = None):
        """Simula el flujo completo de bump para testing"""
        if user is None:
            user = ctx.author
        
        # Simular que el usuario ejecutó /bump
        self.pending_bumps[ctx.guild.id] = user.id
        
        # Simular mensaje de confirmación de DISBOARD
        fake_embed = discord.Embed(
            title="Bump done!",
            description=f"<@{user.id}> bumped the server",
            color=0x00ff00
        )
        
        # Crear un objeto mensaje falso para simular
        class FakeMessage:
            def __init__(self, channel, guild, embeds):
                self.channel = channel
                self.guild = guild
                self.embeds = embeds
                self.author = type('obj', (object,), {'id': DISBOARD_BOT_ID})()
                self.interaction = None
        
        fake_message = FakeMessage(ctx.channel, ctx.guild, [fake_embed])
        
        # Procesar como si fuera un mensaje real de DISBOARD
        await self.disboard_only_bump(fake_message)
        
        await ctx.send(f"✅ **Test iniciado:** Bump simulado para {user.mention}. El recordatorio llegará en {COUNTDOWN} segundos.")

    @commands.command(name="bump_status")
    @commands.has_permissions(administrator=True)
    async def bump_status(self, ctx):
        """Muestra el estado actual de bumps pendientes y tareas activas"""
        embed = discord.Embed(title="📊 Estado del Bump Tracker", color=EMBED_COLOR)
        
        # Bumps pendientes
        if self.pending_bumps:
            pending_list = []
            for guild_id, user_id in self.pending_bumps.items():
                guild_name = self.bot.get_guild(guild_id).name if self.bot.get_guild(guild_id) else f"Guild {guild_id}"
                pending_list.append(f"• **{guild_name}**: <@{user_id}>")
            embed.add_field(name="🕐 Bumps Pendientes", value="\n".join(pending_list), inline=False)
        else:
            embed.add_field(name="🕐 Bumps Pendientes", value="Ninguno", inline=False)
        
        # Tareas activas
        if self.tasks:
            active_list = []
            for guild_id, task in self.tasks.items():
                if not task.done():
                    guild_name = self.bot.get_guild(guild_id).name if self.bot.get_guild(guild_id) else f"Guild {guild_id}"
                    active_list.append(f"• **{guild_name}**: Recordatorio activo")
            if active_list:
                embed.add_field(name="⏰ Recordatorios Activos", value="\n".join(active_list), inline=False)
            else:
                embed.add_field(name="⏰ Recordatorios Activos", value="Ninguno", inline=False)
        else:
            embed.add_field(name="⏰ Recordatorios Activos", value="Ninguno", inline=False)
        
        # Estadísticas generales
        total_bumps = sum(self.bump_data.values())
        embed.add_field(name="📈 Total de Bumps", value=str(total_bumps), inline=True)
        embed.add_field(name="👥 Usuarios Únicos", value=str(len(self.bump_data)), inline=True)
        
        await ctx.send(embed=embed)

    # ────────── comando para clasificación de bumps ──────────
    @commands.command(name="clasificacion")
    async def clasificacion(self, ctx):
        """Muestra el ranking de usuarios por cantidad de bumps"""
        if not self.bump_data:
            await ctx.send("❌ No hay bumps registrados aún.")
            return

        lines = sorted(self.bump_data.items(), key=lambda x: x[1], reverse=True)
        top = "\n".join(
            f"**{i+1}.** <@{uid}> — **{n}** bumps"
            for i, (uid, n) in enumerate(lines[:10])  # top 10
        )

        embed = discord.Embed(
            title="🏆 Clasificación de Bumps",
            description=top,
            color=EMBED_COLOR
        )
        await ctx.send(embed=embed)

    # ───────── estadísticas al iniciar ─────────
    @commands.Cog.listener()
    async def on_ready(self):
        res = ", ".join(f"{u}:{n}" for u, n in self.bump_data.items()) or "sin datos"
        print(f"[BumpTracker] bumps actuales → {res}")

# setup para discord.py v2
async def setup(bot: commands.Bot):
    await bot.add_cog(BumpTracker(bot))