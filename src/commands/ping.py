import logging

import discord
from discord import app_commands


@app_commands.command(name="ping", description="Replies with Pong!")
async def ping(interaction: discord.Interaction):
    __logger.info(f"{interaction.user.id} ({interaction.user.name})")

    await interaction.response.send_message("pong", ephemeral=True)


__logger = logging.getLogger(ping.name)
