from collections import defaultdict
import logging
import io
import json
from os.path import join

import discord
from discord import app_commands
from minify_html import minify

import config
import state as state

from commands.preferences.preferencesUx import *


@app_commands.command(
    name="preferences",
    description="update your preferences with time scheduling",
)
async def preferences(interaction: discord.Interaction):
    userId = interaction.user.id
    __logger.info(f"{userId} ({interaction.user.name})")

    player = state.players[userId]

    player_specs = defaultdict(list[str])
    for spec, raid in player.specs:
        if player.specs[(spec, raid)]:
            player_specs[spec].append(raid)

    data: dict = {
        "specs": state.setup.SPECS,
        "raids": list(state.raids.keys()),
        "timezones": config.timezones,
        "player_timezone": player.timezone,
        "player_specs": dict(player_specs),
        "player_preferences": list(player.preference.values()),
    }

    buf = io.BytesIO(bytes(json.dumps(data, indent=2), "ascii"))
    f = discord.File(buf, filename=f"{interaction.user.name}.json")

    await interaction.response.send_message(
        content=None,
        embed=PreferencesEmbed(),
        view=PreferencesButtons(),
        file=f,
        ephemeral=True,
        delete_after=1800,
    )


__logger = logging.getLogger(preferences.name)
