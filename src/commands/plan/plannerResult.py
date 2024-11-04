from config import *


class PlannerResult:
    def __init__(
        self,
        happiness: float,
        teamToPlayers: list[tuple[PlayerId, Spec]],
        start: Timepoint,
        playhours: list[Timepoint],
    ):
        self.happiness: float = happiness
        self.teamToPlayers: list[tuple[PlayerId, Spec]] = teamToPlayers
        self.start: Timepoint = start
        self.playhours: list[Timepoint] = playhours
