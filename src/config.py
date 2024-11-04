from os import makedirs
from os.path import join, curdir
from datetime import datetime, timedelta, UTC

import logging
import re
import pytz

# Type aliases
Spec = str
Capability = str
Timepoint = int
Preference = int

PlayerId = int
RaidId = str

# Directories
root = curdir
logPath = join(root, "logs")
dataPath = join(root, "data")
assetsPath = join(root, "assets")

playersPath = join(dataPath, "players")
raidsPath = join(dataPath, "raids")

setupPath = join(dataPath, "setup.json")
scheduleTemplatePath = join(assetsPath, "schedule.template.html")

roleName = "Raid Planner"

# Data
maxPreference = 5

timezones = sorted(
    [
        t[4:]
        for t in pytz.all_timezones
        if re.search("^(Etc/GMT\+0)|(Etc/GMT[+-][1-9]+)$", t)
    ],
    key=lambda tz: int(tz[3:]),
)


def initialize():
    logger = logging.getLogger(initialize.__name__)

    logger.info("creating data directories structure ...")
    for d in [
        playersPath,
        raidsPath,
    ]:
        logger.debug(f"... {d}")
        makedirs(d, exist_ok=True)


def new_log_filename():
    return join(logPath, datetime.now().strftime(f"%Y-%m-%d_%H-%M.log"))


def hourToTime(n: int):
    now = datetime.now(UTC)

    d = n // 24
    h = n % 24

    target_day = now + timedelta(days=(d - now.weekday() + 7) % 7)
    target = target_day.replace(hour=h, minute=0, second=0, microsecond=0)

    if target <= now:
        target += timedelta(days=7)

    return target
