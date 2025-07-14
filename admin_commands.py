# admin_commands.py
import discord
from discord.ext import commands
from discord.ui import View, Button
from datetime import datetime, timezone

ROLE_ID      = 1392903420020658196        # ID del rol a añadir/quitar
EMBED_COLOR  = 0x00ffff                   # cyan

# ────────────────────────── Vista y botón persistentes ──────────────────────────
class BumpRoleButton(Button):
    def __init__(self) -> None:
        super().__init__(
            label="🔔 Quiero que me recuerden bumpear",
            style=discord.ButtonStyle.primary,
            custom_id="toggle_bump_role"   # ← necesario para vista persistente
        )

    async def callback(self, interaction: discord.Interaction) -> None:  # type: ignore
        role = interaction.guild.get_role(ROLE_ID)
        if role is None:
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
        # timeout=None + custom_id = vista persistente
        super().__init__(timeout=None)
        self.add_item(BumpRoleButton())

# ────────────────────────── Comandos de administración ──────────────────────────
class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx: commands.Context) -> None:
        """Borra todos los mensajes del canal y confirma."""
        await ctx.channel.purge()
        confirm = await ctx.send("Canal limpiado.")
        await confirm.delete(delay=3)

# ────────────────────────── setup para discord.py v2.x ──────────────────────────
async def setup(bot: commands.Bot) -> None:
    # Añade el cog
    await bot.add_cog(AdminCommands(bot))
    # Registra la vista persistente: necesario para que el botón funcione tras reinicios
    bot.add_view(BumpRoleView())
