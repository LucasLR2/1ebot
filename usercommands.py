import discord
from discord.ext import commands
import json
from datetime import datetime, timezone

class UserCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_commands_channel_id = 1392893710848622734
        self.bump_data_file = "bump_data.json"
        self.bump_data = self.load_bump_data()

        self.rol_entrada_id = 1394791826812043326

    def load_bump_data(self) -> dict:
        try:
            with open(self.bump_data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
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
            description=f"💪 {ctx.author.mention}, actualmente tenés **{bumps}** bumps en total. ¡Excelente trabajo!",
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

        # Buscar producto en tienda
        producto = await self.bot.db.fetchrow(
            "SELECT id, nombre, precio FROM tienda WHERE LOWER(nombre) = $1",
            nombre_objeto
        )
        if not producto:
            await ctx.send("❌ Ese objeto no existe. Usá `!tienda` para ver los productos.")
            return

        # Consultar o crear saldo
        cuenta = await self.bot.db.fetchrow(
            "SELECT balance FROM euros WHERE user_id = $1 AND guild_id = $2",
            user_id, guild_id
        )
        if not cuenta:
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

        # Descontar dinero
        await self.bot.db.execute(
            "UPDATE euros SET balance = balance - $1 WHERE user_id = $2 AND guild_id = $3",
            producto["precio"], user_id, guild_id
        )

        # Verificar si ya tiene el objeto
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

    @commands.command(name='usar')
    async def usar_objeto(self, ctx, *, nombre_objeto: str):
        nombre_objeto = nombre_objeto.lower()
        user_id = str(ctx.author.id)
        guild = ctx.guild

        # Buscar objeto en tienda
        producto = await self.bot.db.fetchrow(
            "SELECT id, nombre FROM tienda WHERE LOWER(nombre) = $1",
            nombre_objeto
        )
        if not producto:
            await ctx.send("❌ Ese objeto no existe.")
            return

        objeto_id = producto['id']
        nombre_real = producto['nombre']

        # Verificar si el usuario tiene el objeto en inventario
        inventario = await self.bot.db.fetchrow(
            "SELECT id, cantidad FROM inventario WHERE usuario_id = $1 AND objeto_id = $2",
            ctx.author.id, objeto_id
        )
        if not inventario or inventario['cantidad'] < 1:
            await ctx.send("❌ No tenés ese objeto en tu inventario.")
            return

        # Restar 1 del inventario o borrar si queda 0
        if inventario['cantidad'] == 1:
            await self.bot.db.execute(
                "DELETE FROM inventario WHERE id = $1",
                inventario['id']
            )
        else:
            await self.bot.db.execute(
                "UPDATE inventario SET cantidad = cantidad - 1 WHERE id = $1",
                inventario['id']
            )

        # Solo para el objeto "entrada" asignar el rol
        if nombre_objeto == "entrada":
            rol = guild.get_role(self.rol_entrada_id)
            if not rol:
                await ctx.send("❌ No se encontró el rol para asignar.")
                return
            try:
                await ctx.author.add_roles(rol, reason=f"Usó el objeto {nombre_real}")
            except discord.Forbidden:
                await ctx.send("❌ No tengo permisos para asignarte el rol.")
                return
            except Exception as e:
                await ctx.send(f"❌ Error al asignar el rol: {e}")
                return
            await ctx.send(f"✅ {ctx.author.mention} usó **{nombre_real}** y se le asignó el rol **{rol.name}**.")
        else:
            await ctx.send(f"✅ {ctx.author.mention} usó **{nombre_real}**.")

async def setup(bot):
    await bot.add_cog(UserCommands(bot))
