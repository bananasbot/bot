from os.path import join
import logging

import discord
from discord import app_commands
from discord.ext import commands

import config


@app_commands.command(name="raid", description="update the raid settings")
@app_commands.describe(raid_file="the raid file")
@commands.has_role(config.roleName)
async def raid(interaction: discord.Interaction, raid_file: discord.Attachment):
    __logger.info(f"{interaction.user.id} ({interaction.user.name})")

    await raid_file.save(join(config.raidsPath, raid_file.filename))
    await interaction.response.send_message("done", ephemeral=True)


__logger = logging.getLogger(raid.name)
