import discord
from discord.ext import commands
import json
from datetime import datetime, timezone

class UserCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_commands_channel_id = 1392893710848622734  # ID real del canal
        self.bump_data_file = "bump_data.json"
        self.bump_data = self.load_bump_data()

    def load_bump_data(self) -> dict:
        try:
            with open(self.bump_data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Aseguramos que las keys sean int (user_id)
            return {int(k): v for k, v in data.items()}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def get_bumps(self, user_id: int) -> int:
        return self.bump_data.get(user_id, 0)

    @commands.command(name="misbumps")
    async def misbumps(self, ctx: commands.Context):
        if ctx.channel.id != self.user_commands_channel_id:
            await ctx.send(f"⚠️ Este comando sólo puede usarse en <#{self.user_commands_channel_id}>.")
            return

        from database import get_bumps

        bumps = await get_bumps(ctx.author.id, ctx.guild.id)

        embed = discord.Embed(
            description=f"💪 {ctx.author.mention}, actualmente tienes **{bumps}** bumps en total. ¡Excelente trabajo!",
            color=0x00ffff,
            timestamp=datetime.now(timezone.utc)
        )
        await ctx.send(embed=embed)

    @commands.command(name='tienda')
    async def ver_tienda(self, ctx):
        productos = await self.bot.db.fetch("SELECT nombre, precio FROM tienda ORDER BY precio ASC")

        if not productos:
            await ctx.send("📦 La tienda está vacía. Esperá a que un admin agregue productos.")
            return

        descripcion = "\n".join([f"• **{p['nombre']}** – {p['precio']}€" for p in productos])

        embed = discord.Embed(
            title="🛒 Productos Disponibles",
            description=descripcion,
            color=discord.Color.purple()
        )
        embed.set_footer(text="Usá !comprar nombre_del_objeto para adquirirlo")
        await ctx.send(embed=embed)

    @commands.command(name='objetos')
    async def ver_objetos(self, ctx, miembro: discord.Member = None):
        miembro = miembro or ctx.author

        objetos = await self.bot.db.fetch("""
            SELECT t.nombre, i.cantidad
            FROM inventario i
            JOIN tienda t ON i.objeto_id = t.id
            WHERE i.usuario_id = $1
        """, miembro.id)

        if not objetos:
            await ctx.send(f"🎒 {miembro.display_name} no tiene objetos todavía.")
            return

        descripcion = "\n".join([f"• {o['nombre']} × {o['cantidad']}" for o in objetos])

        embed = discord.Embed(
            title=f"🎒 Objetos de {miembro.display_name}",
            description=descripcion,
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @commands.command(name='comprar')
    async def comprar_objeto(self, ctx, *, nombre_objeto: str):
        nombre_objeto = nombre_objeto.lower()
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)

        # Obtener el objeto de la tienda
        producto = await self.bot.db.fetchrow(
            "SELECT id, nombre, precio FROM tienda WHERE LOWER(nombre) = $1",
            nombre_objeto
        )

        if not producto:
            await ctx.send("❌ Ese objeto no existe. Usá `!tienda` para ver los productos.")
            return

        # Obtener el saldo del usuario o crear cuenta si no existe
        cuenta = await self.bot.db.fetchrow(
            "SELECT balance FROM euros WHERE user_id = $1 AND guild_id = $2",
            user_id, guild_id
        )

        if not cuenta:
            # Crear cuenta con saldo 0
            await self.bot.db.execute(
                "INSERT INTO euros (user_id, guild_id, balance) VALUES ($1, $2, 0)",
                user_id, guild_id
            )
            balance = 0
        else:
            balance = cuenta["balance"]

        if balance < producto["precio"]:
            await ctx.send(f"💸 No tenés suficiente saldo para comprar **{producto['nombre']}**.")
            return

        # Descontar el precio del objeto
        await self.bot.db.execute(
            "UPDATE euros SET balance = balance - $1 WHERE user_id = $2 AND guild_id = $3",
            producto["precio"], user_id, guild_id
        )

        # Ver si ya tenía el objeto
        existente = await self.bot.db.fetchrow(
            "SELECT id, cantidad FROM inventario WHERE usuario_id = $1 AND objeto_id = $2",
            ctx.author.id, producto['id']
        )

        if existente:
            await self.bot.db.execute(
                "UPDATE inventario SET cantidad = cantidad + 1 WHERE id = $1",
                existente['id']
            )
        else:
            await self.bot.db.execute(
                "INSERT INTO inventario (usuario_id, objeto_id, cantidad) VALUES ($1, $2, 1)",
                ctx.author.id, producto['id']
            )

        nuevo_saldo = balance - producto["precio"]
        await ctx.send(
            f"✅ Has comprado **{producto['nombre']}** por {producto['precio']}€.\n"
            f"💰 Saldo restante: **{nuevo_saldo:.2f}€**"
        )


async def setup(bot):
    await bot.add_cog(UserCommands(bot))
