import os
import logging
import json
from typing import Callable

from config import *

from models.setup import Setup
from models.raid import Raid
from models.player import Player


def load_file[T](reader: Callable, path: str, type) -> T:
    logger = logging.getLogger(load_file.__name__)
    logger.info(f"loading {path} ...")

    res: T = None
    with open(path) as f:
        res = type(reader(f))

    return res


def load_dir[K, V](path: str, key_type, val_type) -> dict[K, V]:
    global setup

    logger = logging.getLogger(load_dir.__name__)
    logger.info(f"loading {path} ...")

    res: dict[K, V] = {}
    for o in os.listdir(path):
        with open(os.path.join(path, o)) as f:
            id: K = key_type(os.path.splitext(o)[0])
            obj: V = val_type(setup, id, json.load(f))
            res[id] = obj
            logger.debug(f"... {id}")

    return res


def reload():
    global setup, players, raids, template

    setup = load_file(json.load, setupPath, Setup.from_json)

    raids = load_dir(raidsPath, str, Raid.from_json)
    players = load_dir(
        playersPath,
        int,
        lambda setup, id, data: Player.from_json(setup, id, raids, data),
    )


setup: Setup
raids: dict[RaidId, Raid]
players: dict[PlayerId, Player]
reload()
