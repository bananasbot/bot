from config import *


class PlannerResult:
    def __init__(
        self,
        happiness,
        players,
        playhours,
        start,
    ):
        self.happiness: float = happiness
        self.start: Timepoint = start
        self.playerToSpec: list[(PlayerId, Spec)] = players
        self.playhours: list[Timepoint] = playhours
