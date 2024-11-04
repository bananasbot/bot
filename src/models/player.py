from .setup import *
import config as config

from models.raid import Raid


class Player:
    def __init__(
        self,
        setup: Setup,
        id: PlayerId,
        raids: list[RaidId],
        specs: dict[Spec, list[RaidId]],
        timezone: str,
        preferences: list[Preference],
    ):
        """Planner params for players"""

        # verify in domain
        if any((p < 0 or config.maxPreference < p) for p in preferences):
            raise f"preference out of bounds"

        self.specs: dict[(Spec, Raid), bool] = {
            (s, r): 0 for s in setup.SPECS for r in raids
        }
        self.specs.update({(s, r): 1 for s in specs for r in specs[s]})
        """classes provided by each player for each raid"""

        self.timezone = timezone
        """the string representation of the timezone"""

        self.timezone_offset: int = int(timezone[3:])
        """the timezone hours offset"""

        self.preference: dict[Timepoint, Preference] = {
            (h + round(self.timezone_offset)) % setup.T: pref
            for h, pref in enumerate(preferences)
        }
        """the timetable, mapping (player,time) to rating (0~1)"""

    @staticmethod
    def from_json(setup: Setup, id: PlayerId, raids: list[RaidId], data: dict):
        return Player(
            setup,
            id=id,
            raids=raids,
            specs=data.get("specs"),
            preferences=data.get("preferences"),
            timezone=data.get("timezone"),
        )
