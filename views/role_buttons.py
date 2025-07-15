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

class VerificacionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ Verificarse", style=discord.ButtonStyle.success, custom_id="verificar_button")
    async def verificar(self, interaction: discord.Interaction, button: discord.ui.Button):
        rol_id = 1391832974361886740
        rol = interaction.guild.get_role(rol_id)

        if rol is None:
            await interaction.response.send_message(
                "❌ No se encontró el rol de verificación. Contacta a un administrador.",
                ephemeral=True
            )
            return

        if rol in interaction.user.roles:
            await interaction.response.send_message(
                "⚠️ Ya estás verificado.",
                ephemeral=True
            )
        else:
            await interaction.user.add_roles(rol)
            await interaction.response.send_message(
                "✅ ¡Has sido verificado correctamente!",
                ephemeral=True
            )

class VerAvisosView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(emoji="🔔", label="Notificaciones", style=discord.ButtonStyle.primary, custom_id="rol_avisos")
    async def toggle_notificaciones(self, interaction: discord.Interaction, button: discord.ui.Button):
        rol_id = 1394757542919540776
        rol = interaction.guild.get_role(rol_id)

        if rol is None:
            await interaction.response.send_message("❌ No encontré el rol de notificaciones. Contactá a un admin.", ephemeral=True)
            return

        if rol in interaction.user.roles:
            await interaction.response.send_message("⚠️ Ya tenés el rol de notificaciones.", ephemeral=True)
        else:
            await interaction.user.add_roles(rol)
            await interaction.response.send_message("✅ Ahora vas a recibir notificaciones.", ephemeral=True)
