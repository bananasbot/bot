from .setup import *


class Raid:
    def __init__(
        self,
        setup: Setup,
        id: RaidId,
        name: str,
        length: int,
        min_people: int,
        max_people: int,
        min_requirements: dict[Capability, int],
        max_requirements: dict[Capability, int],
    ):
        """Planner params for raid"""

        self.id = id
        """the raid id"""

        self.name = name
        """expanded raid name"""

        self.length = length
        """expected raid duration, in hours"""

        self.min_people = min_people
        """min amount of people"""

        self.max_people = max_people
        """max amount of people"""

        self.min_requirements = {c: 0 for c in setup.CAPABILITIES}
        self.min_requirements.update(min_requirements)
        """the minimum capabilities required by the raid"""

        self.max_requirements = {c: max_people for c in setup.CAPABILITIES}
        self.max_requirements.update(max_requirements)
        """the maximum amount for a requirement"""

        # verify
        for c in setup.CAPABILITIES:
            if not (self.min_requirements[c] <= self.max_requirements[c]):
                raise f"min requirement ({self.min_requirements[c]}) must be <= than max requirement ({self.max_requirements[c]})"

        for c in setup.CAPABILITIES:
            if self.min_requirements[c] > self.max_people:
                raise f"min requirement ({self.min_requirements[c]}) must be <= than max people ({self.max_people})"
            if self.max_requirements[c] < 0:
                raise f"max requirement ({self.max_requirements[c]}) must be > than 0"

    @staticmethod
    def from_json(setup: Setup, id: RaidId, data: dict):
        return Raid(
            setup,
            id=id,
            name=data.get("name"),
            length=int(data.get("length")),
            min_people=int(data.get("min_people")),
            max_people=int(data.get("max_people")),
            min_requirements=data.get("min_requirements"),
            max_requirements=data.get("max_requirements"),
        )
