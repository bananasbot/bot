import logging
import dotenv


dotenv.load_dotenv()

from discord.app_commands import AppCommand
from discord.ext.commands import Command, Bot

from commands.reload import reload
from commands.ping import ping
from commands.preferences.preferences import preferences
from commands.plan.plan import plan
from commands.raid import raid

commands: list[Command] = [
    ping,
    preferences,
    plan,
    reload,
    raid,
]


async def setup_commands(bot: Bot):
    logger = logging.getLogger(setup_commands.__name__)

    # logger.info("removing all commands ...")
    # old_commands: list[AppCommand] = [
    #     *await bot.tree.fetch_commands(),
    #     *await bot.tree.fetch_commands(guild=Idable(int(os.getenv("GUILD_ID")))),
    # ]
    # await asyncio.gather(*[del_command(logger, c) for c in old_commands])

    logger.info("adding back all commands ...")
    for command in commands:
        bot.tree.add_command(command)
        logger.debug(f"... {command.name}")

    logger.info("syncing slash commands ...")
    await bot.tree.sync()


class Idable:
    def __init__(self, id):
        self.id = id


def del_command(logger: logging.Logger, c: AppCommand):
    logger.debug(f"... {c.name}")
    return c.delete()
