import logging

import discord
from discord import app_commands
from discord.ext import commands

import config
import state


@app_commands.command(name="reload", description="reload the state")
@commands.has_role(config.roleName)
async def reload(interaction: discord.Interaction):
    __logger.info(f"{interaction.user.id} ({interaction.user.name})")

    state.reload()
    await interaction.response.send_message("done", ephemeral=True)


__logger = logging.getLogger(reload.name)
