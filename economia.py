import discord
from discord.ext import commands
import asyncpg
import os
import logging
from contextlib import asynccontextmanager
from typing import Optional

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_URL = os.getenv("DATABASE_URL")

MAX_AMOUNT = 1000000.0
MIN_AMOUNT = 0.01

def format_currency(amount: float) -> str:
    return f"€{amount:,.2f}"

async def connect():
    try:
        return await asyncpg.connect(DB_URL)
    except Exception as e:
        logger.error(f"Error conectando a la base de datos: {e}")
        raise

@asynccontextmanager
async def get_connection():
    conn = None
    try:
        conn = await connect()
        yield conn
    except Exception as e:
        logger.error(f"Error en conexión de base de datos: {e}")
        raise
    finally:
        if conn:
            await conn.close()

class Economia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def ensure_user(self, user_id: str, guild_id: str) -> bool:
        try:
            async with get_connection() as conn:
                await conn.execute("""
                    INSERT INTO euros (user_id, guild_id, balance)
                    VALUES ($1, $2, 0)
                    ON CONFLICT (user_id, guild_id) DO NOTHING;
                """, user_id, guild_id)
            return True
        except Exception as e:
            logger.error(f"Error en ensure_user: {e}")
            return False

    async def get_balance(self, user_id: str, guild_id: str) -> Optional[float]:
        try:
            async with get_connection() as conn:
                row = await conn.fetchrow("""
                    SELECT balance FROM euros
                    WHERE user_id = $1 AND guild_id = $2;
                """, user_id, guild_id)
                return row["balance"] if row else None
        except Exception as e:
            logger.error(f"Error obteniendo balance: {e}")
            return None

    def validate_amount(self, amount: float) -> tuple[bool, str]:
        if amount < MIN_AMOUNT:
            return False, f"❌ El monto mínimo es {format_currency(MIN_AMOUNT)}."
        if amount > MAX_AMOUNT:
            return False, f"❌ El monto máximo es {format_currency(MAX_AMOUNT)}."
        return True, ""

    @commands.command(name="adde")
    @commands.has_permissions(administrator=True)
    async def adde(self, ctx, member: discord.Member, amount: float):
        """Agrega euros a un usuario (solo admins)."""
        valid, error_msg = self.validate_amount(amount)
        if not valid:
            await ctx.send(error_msg)
            return

        guild_id = str(ctx.guild.id)
        user_id = str(member.id)

        if not await self.ensure_user(user_id, guild_id):
            await ctx.send("❌ Error al acceder a la base de datos.")
            return

        try:
            async with get_connection() as conn:
                await conn.execute("""
                    UPDATE euros
                    SET balance = balance + $1
                    WHERE user_id = $2 AND guild_id = $3;
                """, amount, user_id, guild_id)

            embed = discord.Embed(
                title="Saldo Modificado",
                description=f"Se añadieron:\n\n```{format_currency(amount)}```\na {member.mention}.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            logger.info(f"Admin {ctx.author.id} añadió {amount} a {member.id} en guild {guild_id}")

        except Exception as e:
            logger.error(f"Error en comando adde: {e}")
            await ctx.send("❌ Error al procesar la transacción.")

    @commands.command(name="removee")
    @commands.has_permissions(administrator=True)
    async def removee(self, ctx, member: discord.Member, amount: float):
        """Remueve euros de un usuario (solo admins)."""
        valid, error_msg = self.validate_amount(amount)
        if not valid:
            await ctx.send(error_msg)
            return

        guild_id = str(ctx.guild.id)
        user_id = str(member.id)

        if not await self.ensure_user(user_id, guild_id):
            await ctx.send("❌ Error al acceder a la base de datos.")
            return

        try:
            async with get_connection() as conn:
                current_balance = await self.get_balance(user_id, guild_id)
                if current_balance is None:
                    await ctx.send("❌ Error al obtener el balance del usuario.")
                    return

                new_balance = max(0, current_balance - amount)
                removed_amount = current_balance - new_balance

                await conn.execute("""
                    UPDATE euros
                    SET balance = $1
                    WHERE user_id = $2 AND guild_id = $3;
                """, new_balance, user_id, guild_id)

            embed = discord.Embed(
                title="Saldo Modificado",
                description=f"Se removieron:\n\n```{format_currency(removed_amount)}```\nde {member.mention}.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            logger.info(f"Admin {ctx.author.id} removió {removed_amount} de {member.id} en guild {guild_id}")

        except Exception as e:
            logger.error(f"Error en comando removee: {e}")
            await ctx.send("❌ Error al procesar la transacción.")

    @commands.command(name="reset_economia")
    @commands.has_permissions(administrator=True)
    async def reset_economia(self, ctx):
        """Resetea toda la economía del servidor (solo admins)."""
        guild_id = str(ctx.guild.id)

        embed = discord.Embed(
            title="⚠️ Confirmación Requerida",
            description="¿Estás seguro de que quieres resetear toda la economía del servidor?\n\n**Esta acción no se puede deshacer.**",
            color=discord.Color.red()
        )

        msg = await ctx.send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == msg.id

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=30.0, check=check)

            if str(reaction.emoji) == "✅":
                async with get_connection() as conn:
                    await conn.execute("""
                        DELETE FROM euros WHERE guild_id = $1;
                    """, guild_id)

                await ctx.send("🔄 Economía del servidor reseteada exitosamente.")
                logger.info(f"Admin {ctx.author.id} reseteó la economía del guild {guild_id}")
            else:
                await ctx.send("❌ Operación cancelada.")

        except Exception as e:
            logger.error(f"Error en reset_economia: {e}")
            await ctx.send("❌ Error al resetear la economía.")

    # Los otros comandos ya están en tu código original (dar, banco, top, cuenta)

    @commands.command(name="banco")
    async def banco(self, ctx):
        guild_id = str(ctx.guild.id)
        user_id = str(ctx.author.id)

        if not await self.ensure_user(user_id, guild_id):
            await ctx.send("❌ Error al acceder a la base de datos.")
            return

        balance = await self.get_balance(user_id, guild_id)
        if balance is None:
            await ctx.send("❌ Error al obtener tu balance.")
            return

        embed = discord.Embed(
            title="Estado de Cuenta",
            description=f"{ctx.author.mention}, tienes:\n\n```{format_currency(balance)}```",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @commands.command(name="dar")
    async def dar(self, ctx, member: discord.Member, amount: float):
        if member.id == ctx.author.id:
            await ctx.send("❌ No puedes darte dinero a ti mismo.")
            return

        if member.bot:
            await ctx.send("❌ No puedes dar dinero a un bot.")
            return

        valid, error_msg = self.validate_amount(amount)
        if not valid:
            await ctx.send(error_msg)
            return

        guild_id = str(ctx.guild.id)
        sender_id = str(ctx.author.id)
        receiver_id = str(member.id)

        if not await self.ensure_user(sender_id, guild_id):
            await ctx.send("❌ Error al acceder a la base de datos.")
            return
        if not await self.ensure_user(receiver_id, guild_id):
            await ctx.send("❌ Error al acceder a la base de datos.")
            return

        try:
            async with get_connection() as conn:
                async with conn.transaction():
                    sender = await conn.fetchrow("""
                        SELECT balance FROM euros WHERE user_id = $1 AND guild_id = $2;
                    """, sender_id, guild_id)

                    if not sender or sender["balance"] < amount:
                        await ctx.send(f"❌ No tienes suficiente dinero. Balance actual:\n```{format_currency(sender['balance'] if sender else 0)}```")
                        return

                    await conn.execute("""
                        UPDATE euros SET balance = balance - $1 WHERE user_id = $2 AND guild_id = $3;
                    """, amount, sender_id, guild_id)

                    await conn.execute("""
                        UPDATE euros SET balance = balance + $1 WHERE user_id = $2 AND guild_id = $3;
                    """, amount, receiver_id, guild_id)

            embed = discord.Embed(
                title="Transferencia Exitosa",
                description=f"{ctx.author.mention} le dio:\n\n```{format_currency(amount)}```\na {member.mention}.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)

        except Exception as e:
            logger.error(f"Error en comando dar: {e}")
            await ctx.send("❌ Error al procesar la transferencia.")

    @commands.command(name="top")
    async def top(self, ctx, limit: int = 10):
        if limit < 1 or limit > 20:
            await ctx.send("❌ El límite debe estar entre 1 y 20.")
            return

        guild_id = str(ctx.guild.id)

        try:
            async with get_connection() as conn:
                rows = await conn.fetch("""
                    SELECT user_id, balance FROM euros
                    WHERE guild_id = $1 AND balance > 0
                    ORDER BY balance DESC
                    LIMIT $2;
                """, guild_id, limit)

            if not rows:
                await ctx.send("🏦 No hay usuarios en el ranking aún.")
                return

            description = ""
            medals = ["🥇", "🥈", "🥉"]

            for i, row in enumerate(rows, start=1):
                user = ctx.guild.get_member(int(row["user_id"]))
                name = user.display_name if user else "Usuario desconocido"
                medal = medals[i-1] if i <= 3 else f"**#{i}**"
                description += f"{medal} {name} — ```{format_currency(row['balance'])}```\n"

            embed = discord.Embed(
                title=f"Top {len(rows)} - Banco del Servidor",
                description=description,
                color=discord.Color.gold()
            )
            embed.set_footer(text=f"Solicitado por {ctx.author.display_name}")
            await ctx.send(embed=embed)

        except Exception as e:
            logger.error(f"Error en comando top: {e}")
            await ctx.send("❌ Error al obtener el ranking.")

    @commands.command(name="cuenta")
    async def cuenta(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        guild_id = str(ctx.guild.id)
        user_id = str(target.id)

        if not await self.ensure_user(user_id, guild_id):
            await ctx.send("❌ Error al acceder a la base de datos.")
            return

        balance = await self.get_balance(user_id, guild_id)
        if balance is None:
            await ctx.send("❌ Error al obtener el balance.")
            return

        embed = discord.Embed(
            title="Consulta de Balance",
            description=f"{target.mention} tiene:\n\n```{format_currency(balance)}```",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    # Manejo de errores
    @adde.error
    @removee.error
    @dar.error
    async def economy_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Faltan argumentos. Usa `!help <comando>` para ver la sintaxis.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ No tienes permisos para usar este comando.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Formato inválido. Asegúrate de mencionar al usuario y usar un número válido.")
        else:
            logger.error(f"Error no manejado en economía: {error}")
            await ctx.send("❌ Ocurrió un error inesperado.")

async def setup(bot):
    await bot.add_cog(Economia(bot))
