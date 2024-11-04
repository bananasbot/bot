import os
import logging
import dotenv


dotenv.load_dotenv()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


import config

logger.info("ensuring directory structure ...")
for d in [
    config.playersPath,
    config.raidsPath,
    config.logPath,
]:
    logger.debug(f"... '{d}'")
    os.makedirs(d, exist_ok=True)

logfile = config.new_log_filename()
logger.info(f"will write logs to '{logfile}'")
logging.basicConfig(filename=logfile, level=logging.DEBUG, force=True)


logger.info("resuming state ...")
import state


logger.info("initializing bot ...")
import bot
