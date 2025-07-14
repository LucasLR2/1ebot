# views/role_buttons.py

import discord

class RoleButtonView(discord.ui.View):
    def __init__(self, role_id: int):
        super().__init__(timeout=None)
        self.role_id = role_id

    @discord.ui.button(
        label="🎖️ Quiero el rol",
        style=discord.ButtonStyle.blurple,
        custom_id="get_role_button"
    )
    async def give_role_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(self.role_id)

        if not role:
            await interaction.response.send_message("⚠️ Rol no encontrado.", ephemeral=True)
            return

        if role in interaction.user.roles:
            await interaction.response.send_message("Ya tenés este rol 😉", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"✅ ¡Rol `{role.name}` asignado!", ephemeral=True)
