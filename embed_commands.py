import discord
from discord.ext import commands
from datetime import datetime, timezone
import asyncio
from views.role_buttons import RoleButtonView, VerificacionView, VerAvisosView

BUMPER_ROLE_ID = 1392903420020658196
RESEÑADOR_ROLE_ID = 1394444010436956316

class EmbedCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ereglas')
    @commands.has_permissions(administrator=True)
    async def reglas_embed(self, ctx):
        embed = discord.Embed(
            title="💥 𝑹𝑬𝑮𝑳𝑨𝑺 – Sorteos y Torneos",
            description=(
                "🎉 **¡Bienvenid@ al servidor oficial de Brawl Pass Plus!**\n"
                "Aquí podés participar en sorteos, torneos y ganar premios increíbles. Leé esto antes de empezar:\n"
                "⸻\n"
                "💸 **Participación:**\n"
                "• Cada entrada cuesta **1 €**.\n"
                "• El evento comienza al llegar a **10 participantes**.\n"
                "• Podés elegir entre **sorteo aleatorio** o **torneo competitivo**.\n"
                "⸻\n"
                "🎁 **Premios:**\n"
                "• El ganador se lleva un **Brawl Pass Plus**.\n"
                "• ¡Los que no ganan acumulan **1 punto** por intento!\n"
                "⸻\n"
                "🔁 **Fidelidad:**\n"
                "• Si acumulás **10 intentos sin ganar**, recibís un pase **totalmente GRATIS**.\n"
                "• El contador se reinicia al ganar o recibir un pase.\n"
                "⸻\n"
                "🛍️ **Compra directa:**\n"
                "• ¿Preferís no esperar? Comprá un **Brawl Pass Plus por 9 €** en cualquier momento.\n"
                "⸻\n"
                "🎯 **¡Conseguí entradas GRATIS!**\n"
                "• Haciendo distintas **actividades dentro del servidor** también podés ganar **participaciones gratuitas**.\n"
                "⸻\n"
                "⚠️ **Importante:**\n"
                "• Cada entrada vale solo para el evento en curso.\n"
                "• No se permiten reembolsos ni trampas.\n"
                "• Respeto y honestidad son obligatorios.\n"
                "⸻\n"
                "❓ ¿Dudas? Abrí un ticket o hablá con un moderador.\n"
                "¡Gracias por ser parte de la comunidad y mucha suerte! 🍀"
            ),
            color=discord.Color.purple()
        )
        embed.set_footer(text="1€Bot • Sistema de Sorteos y Torneos")
        await ctx.send(embed=embed)

    @commands.command(name='ebs')
    @commands.has_permissions(administrator=True)
    async def canal_brawlstars(self, ctx):
        embed = discord.Embed(
            title="👾 𝑩𝑹𝑨𝑾𝑳 𝑺𝑻𝑨𝑹𝑺 – Canal Oficial",
            description=(
                "🎮 En **【👾-𝙱𝚁𝙰𝚆𝙻-𝚂𝚃𝙰𝚁𝚂】** podés hablar sobre todo lo relacionado al juego.\n"
                "• Compartí tus logros, estrategias y momentos épicos.\n"
                "• Usá **bots interactivos** para estadísticas, minijuegos y más.\n"
                "• Participá con la comunidad y pasala bien 💬🔥"
            ),
            color=discord.Color.purple()
        )
        embed.set_footer(text="1€Bot • Comunidad Activa de Brawl Stars")
        await ctx.send(embed=embed)

    @commands.command(name='eniveles')
    @commands.has_permissions(administrator=True)
    async def niveles_embed(self, ctx):
        embed = discord.Embed(
            title="🚀 𝑺𝑰𝑺𝑻𝑬𝑴𝑨 𝑫𝑬 𝑵𝑰𝑽𝑬𝑳𝑬𝑺",
            description=(
                "📈 En **【🚀-𝙽𝙸𝚅𝙴𝙻𝙴𝚂】** subís de nivel participando activamente en el servidor:\n"
                "• Hablá, compartí y ayudá para ganar **XP**.\n"
                "• Al subir de nivel, desbloqueás **roles exclusivos**.\n"
                "⸻\n"
                "🏅 **Roles por nivel:**\n"
                "Nivel 1 – <@&1392553078154334268>\n"
                "Nivel 5 – <@&1392527877618270381>\n"
                "Nivel 10 – <@&1392528406213693450>\n"
                "Nivel 15 – <@&1392528504456740907>\n"
                "Nivel 20 – <@&1392528639282905198>\n"
                "Nivel 25 – <@&1392528597163446272>\n"
                "Nivel 30 – <@&1392528831486759102>\n"
                "Nivel 35 – <@&1392529090220921082>\n"
                "Nivel 40 – <@&1392529254293700669>\n"
                "Nivel 45 – <@&1392529399558963231>\n"
                "Nivel 50 – <@&1392529675003105301>\n"
                "Nivel 55 – <@&1392529783568732263>\n"
                "Nivel 60 – <@&1392529859758002236>\n"
                "Nivel 65 – <@&1392529960635465890>\n"
                "Nivel 70 – <@&1392530121243627580>\n"
                "Nivel 75 – <@&1392530294925693058>\n"
                "Nivel 80 – <@&1392530401997619312>\n"
                "Nivel 85 – <@&1392530505655914577>\n"
                "Nivel 90 – <@&1392530714628456478>\n"
                "Nivel 95 – <@&1392530788788211863>\n"
                "Nivel 100 – <@&1392530888256127016>"
            ),
            color=discord.Color.purple()
        )
        embed.set_footer(text="1€Bot • ¡Subí de nivel y destacate!")
        await ctx.send(embed=embed)

    @commands.command(name='ebump')
    @commands.has_permissions(administrator=True)
    async def bump_embed(self, ctx):
        embed = discord.Embed(
            title="🚀 𝑩𝑼𝑴𝑷 – ¡Ayudá al servidor a crecer!",
            description=(
                "🔝 Usá **`/bump`** para subir el servidor en los listados.\n"
                "📊 Consultá tu progreso con **`!misbumps`**.\n"
                "🏆 Revisá la **clasificación global** con **`!clasificacion`**.\n"
                "🎁 ¡Muy pronto vas a poder canjear tus bumps por **recompensas** exclusivas!"
            ),
            color=discord.Color.purple(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_footer(text="1€Bot • Sistema de Bumps")
        await ctx.send(embed=embed, view=RoleButtonView(BUMPER_ROLE_ID))

    @commands.command(name='eresenas')
    @commands.has_permissions(administrator=True)
    async def resenas_embed(self, ctx):
        embed = discord.Embed(
            title="📝 𝑹𝑬𝑺𝑬Ñ𝑨𝑺 – ¡Ganá sin pagar!",
            description=(
                "🆓 ¿Querés participar **gratis** en un sorteo o torneo?\n"
                "¡Solo necesitás hacer algunas **reseñas simples**!\n"
                "⸻\n"
                "✍️ Nosotros te indicamos cuáles, vos las completás.\n"
                "🎁 Participás sin pagar y seguís acumulando puntos hacia tu **premio asegurado**.\n"
                "💡 Es fácil, rápido y te da ventaja en los eventos.\n"
                "⸻\n"
                "💬 Pedí tus reseñas disponibles a un staff o en el canal correspondiente."
            ),
            color=discord.Color.purple()
        )
        embed.set_footer(text="1€Bot • ¡Participá gratis con reseñas!")
        await ctx.send(embed=embed, view=RoleButtonView(RESEÑADOR_ROLE_ID))

    @commands.command(name="everificacion")
    @commands.has_permissions(administrator=True)
    async def everificacion(self, ctx):
        embed = discord.Embed(
            title="🔒 Verificación",
            description="Haz clic en el botón de abajo para verificarte y acceder al resto del servidor.",
            color=discord.Color.green()
        )
        embed.set_footer(text="Sistema de verificación • 1ebot")

        view = VerificacionView()
        await ctx.send(embed=embed, view=view)

    @commands.command(name="eeconomia")
    @commands.has_permissions(administrator=True)
    async def eeconomia(self, ctx):
        canal_id = 1395050940486385734
        canal_destino = ctx.guild.get_channel(canal_id)

        if canal_destino is None:
            await ctx.send("❌ No pude encontrar el canal de economía. Revisá el ID.")
            return

        embed = discord.Embed(
            title="𝙱𝙰𝙽𝙲𝙾",
            description=(
                "Aquí puedes consultar tu saldo y hacer transferencias.\n\n"
                "**Comandos disponibles:**\n"
                "`!cuenta` - Consulta tu saldo o el de otro usuario.\n"
                "`!dar @usuario cantidad` - Envía euros a otro usuario.\n"
                "`!top [n]` - Muestra el ranking de los usuarios con más euros (máx 20).\n"
            ),
            color=discord.Color.green()
        )
        embed.set_footer(text="Economía • 1€Bot")

        await canal_destino.send(embed=embed)
        await ctx.send("✅ Aviso de economía enviado correctamente.")

    @commands.command(name="eresena")
    @commands.has_permissions(administrator=True)
    async def aviso_resena(self, ctx, cantidad: int = 2): 
        rol_id_mencion = 1394444010436956316
        canal_id_aviso = 1394797177351573514

        rol_mencion = ctx.guild.get_role(rol_id_mencion)
        canal_destino = ctx.guild.get_channel(canal_id_aviso)

        try:
            if canal_destino is None:
                await ctx.send("❌ No pude encontrar el canal de avisos. Revisá el ID.")
                return

            embed = discord.Embed(
                title="📢 ¡Nuevas reseñas disponibles!",
                description=f"Hay {cantidad} reseña{'s' if cantidad != 1 else ''} disponible{'s' if cantidad != 1 else ''}, abre ticket para hacerla{'s' if cantidad != 1 else ''} y ganar '€'",
                color=discord.Color.orange()
            )
            embed.set_footer(text="Aviso del staff • 1€Bot")

            if rol_mencion:
                await canal_destino.send(content=rol_mencion.mention, embed=embed)
            else:
                await canal_destino.send(embed=embed)

            await ctx.send("✅ Aviso enviado correctamente al canal designado.")

        except Exception as e:
            await ctx.send(f"❌ Ocurrió un error: {str(e)}")



    @commands.command(name="aviso")
    @commands.has_permissions(administrator=True)
    async def aviso(self, ctx):
        rol_id_mencion = 1394757542919540776
        canal_id_aviso = 1391833217815941253

        rol_mencion = ctx.guild.get_role(rol_id_mencion)
        canal_destino = ctx.guild.get_channel(canal_id_aviso)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            # Verificar si el canal existe antes de continuar
            if canal_destino is None:
                await ctx.send("❌ No pude encontrar el canal de avisos. Revisá el ID.")
                return

            await ctx.send("📌 ¿Cuál es el **título** del aviso?")
            titulo_msg = await self.bot.wait_for('message', check=check, timeout=60)
            titulo = titulo_msg.content

            await ctx.send("📝 ¿Cuál es la **descripción** del aviso?")
            desc_msg = await self.bot.wait_for('message', check=check, timeout=120)
            descripcion = desc_msg.content

            embed = discord.Embed(
                title=titulo,
                description=descripcion,
                color=discord.Color.orange()
            )
            embed.set_footer(text="Aviso del staff • 1€Bot")

            view = VerAvisosView()

            # Enviar el aviso al canal
            if rol_mencion:
                await canal_destino.send(content=rol_mencion.mention, embed=embed, view=view)
            else:
                await canal_destino.send(embed=embed, view=view)

            # Confirmar al usuario
            await ctx.send("✅ Aviso enviado correctamente al canal designado.")

        except asyncio.TimeoutError:
            await ctx.send("⌛ Se acabó el tiempo. Ejecutá `!aviso` de nuevo.")
        except Exception as e:
            await ctx.send(f"❌ Ocurrió un error: {str(e)}")

    @commands.command(name='efuncionamiento')
    @commands.has_permissions(administrator=True)
    async def canal_funcionamiento(self, ctx):
        # Reemplazá estos IDs por los reales
        canal_banco_id = 1395050940486385734  # 💸-banco
        canal_tienda_id = 1395783024662024223  # 🛒-tienda
        canal_resenas_id = 1394797177351573514  # 📝-reseñas

        # Referencias de canales
        canal_banco = ctx.guild.get_channel(canal_banco_id)
        canal_tienda = ctx.guild.get_channel(canal_tienda_id)
        canal_resenas = ctx.guild.get_channel(canal_resenas_id)

        embed = discord.Embed(
            title="💸 𝑭𝑼𝑵𝑪𝑰𝑶𝑵𝑨𝑴𝑰𝑬𝑵𝑻𝑶 – Economía del Servidor",
            description=(
                "📌 En esta sección vas a encontrar todo lo relacionado con la **economía interna** del servidor.\n\n"
                f"En {canal_banco.mention} podés:\n"
                "• Consultar tu saldo y el de otros miembros.\n"
                "• Pasar € a otros usuarios de forma rápida.\n"
                "• Ver el top económico del servidor.\n\n"
                f"En {canal_tienda.mention}:\n"
                "• Encontrás todos los productos disponibles.\n"
                "• Cada uno con su precio correspondiente en €.\n\n"
                f"En {canal_resenas.mention}:\n"
                "• Podés escribir reseñas y generar € gratis.\n"
                "• Cuanto mejor sea tu reseña, mayor la recompensa.\n\n"
                "¿Por qué usamos esto?\n"
                "Para que puedas **participar en eventos** y obtener **recompensas gratis** sin necesidad de usar dinero real 🤑🎁"
            ),
            color=discord.Color.gold()
        )
        embed.set_footer(text="1€Bot • Sistema de economía")
        await ctx.send(embed=embed)

# ──────────────────────── Setup para discord.py v2.x ────────────────────────
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(EmbedCommands(bot))
