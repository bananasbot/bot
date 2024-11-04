import os
import logging

from discord import Color, Guild, Intents
from discord.ext import commands as ks

import config

from commands.commands import setup_commands

intents = Intents.none()
intents.guilds = True

bot = ks.Bot(command_prefix="noprefix", intents=intents)


@bot.event
async def on_ready():
    logger = logging.getLogger(on_ready.__name__)
    logger.info(f"logged in as {bot.user.name}")

    await setup_commands(bot)

    logger.info("ready to go!")
    print("ready to go!")


@bot.event
async def on_guild_join(guild: Guild):
    logger = logging.getLogger(on_guild_join.__name__)
    logger.info("creating raid management role ...")
    await guild.create_role(
        name=config.roleName,
        color=Color.dark_orange(),
        mentionable=False,
        reason="Required role to invoke the raid-management slash commands",
    )


bot.run(os.getenv("DISCORD_TOKEN"))
