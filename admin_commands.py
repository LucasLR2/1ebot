# admin_commands.py
import asyncpg
import discord
from discord.ext import commands
from discord.ui import View, Button
from datetime import datetime, timezone

ROLE_ID     = 1392903420020658196   # ID del rol para recordar bumps
EMBED_COLOR = 0x00ffff              # Cyan

# ────────────────────────── Vista persistente y botón ──────────────────────────
class BumpRoleButton(Button):
    def __init__(self) -> None:
        super().__init__(
            label="🔔 Quiero que me recuerden bumpear",
            style=discord.ButtonStyle.primary,
            custom_id="toggle_bump_role"
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        role = interaction.guild.get_role(ROLE_ID)
        if not role:
            await interaction.response.send_message(
                "❌ No se encontró el rol.", ephemeral=True
            )
            return

        member = interaction.user
        if role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message(
                "🚫 Ya no recibirás recordatorios de bump.", ephemeral=True
            )
        else:
            await member.add_roles(role)
            await interaction.response.send_message(
                "✅ ¡Ahora recibirás recordatorios de bump!", ephemeral=True
            )

class BumpRoleView(View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(BumpRoleButton())

# ────────────────────────── Comandos Admin ──────────────────────────
class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # ────────── !clear ──────────
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx: commands.Context, cantidad: int = None) -> None:
        """Borra mensajes del canal"""
        if cantidad is None:
            await ctx.channel.purge()
            confirm = await ctx.send("🧹 Canal limpiado completamente.")
        else:
            deleted = await ctx.channel.purge(limit=cantidad + 1)
            confirm = await ctx.send(f"✅ Se eliminaron {len(deleted) - 1} mensajes.")
        await confirm.delete(delay=3)

    # ────────── !setbumps ──────────
    @commands.command(name="setbumps")
    @commands.has_permissions(administrator=True)
    async def set_bumps(self, ctx, user: discord.Member, cantidad: int):
        await self.bot.db.execute('''
            INSERT INTO bumps (user_id, guild_id, count)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id, guild_id)
            DO UPDATE SET count = $3;
        ''', str(user.id), str(ctx.guild.id), cantidad)
        await ctx.send(f"✅ Se establecieron **{cantidad}** bumps para {user.mention}.")

    # ────────── !addobj ──────────
    @commands.command(name='addobj')
    @commands.has_permissions(administrator=True)
    async def agregar_objeto(self, ctx, nombre: str, precio: int):
        try:
            await self.bot.db.execute(
                "INSERT INTO tienda (nombre, precio) VALUES ($1, $2)",
                nombre, precio
            )
            await ctx.send(f"✅ Objeto **{nombre}** agregado a la tienda por **{precio}€**.")
        except asyncpg.UniqueViolationError:
            await ctx.send("❌ Ese objeto ya existe en la tienda.")
        except Exception as e:
            await ctx.send(f"⚠️ Error al agregar el objeto: `{e}`")

    # ────────── !editobj ──────────
    @commands.command(name='editobj')
    @commands.has_permissions(administrator=True)
    async def editar_objeto(self, ctx, nombre: str, nuevo_precio: int):
        resultado = await self.bot.db.execute(
            "UPDATE tienda SET precio = $1 WHERE nombre = $2",
            nuevo_precio, nombre
        )
        if resultado == "UPDATE 0":
            await ctx.send("❌ No se encontró un objeto con ese nombre.")
        else:
            await ctx.send(f"✏️ El objeto **{nombre}** ahora cuesta **{nuevo_precio}€**.")

    # ────────── !delobj ──────────
    @commands.command(name='delobj')
    @commands.has_permissions(administrator=True)
    async def eliminar_objeto(self, ctx, nombre: str):
        resultado = await self.bot.db.execute(
            "DELETE FROM tienda WHERE nombre = $1",
            nombre
        )
        if resultado == "DELETE 0":
            await ctx.send("❌ No se encontró un objeto con ese nombre.")
        else:
            await ctx.send(f"🗑️ El objeto **{nombre}** fue eliminado de la tienda.")

# ────────────────────────── Setup ──────────────────────────
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AdminCommands(bot))
    bot.add_view(BumpRoleView())  # Vista persistente para el botón
