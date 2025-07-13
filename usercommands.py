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

        bumps = self.get_bumps(ctx.author.id)
        embed = discord.Embed(
            description=f"💪 {ctx.author.mention}, actualmente tienes **{bumps}** bumps en total. ¡Excelente trabajo!",
            color=0x00ffff,
            timestamp=datetime.now(timezone.utc)
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UserCommands(bot))
