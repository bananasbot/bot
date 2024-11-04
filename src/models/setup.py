from config import *


class Setup:
    def __init__(
        self,
        timepoints: int,
        specs: list[Spec],
        capabilities: list[Capability],
        spec_can: dict[tuple[Spec, Capability], bool],
    ):
        """Planner params for players"""

        self.T: int
        """amount of timepoints"""

        self.TIMEPOINTS: list[Timepoint]
        """actual timepoints"""

        self.SPECS: list[Spec]
        """the existing (sub)specializations"""

        self.CAPABILITIES: list[Capability]
        """the list of capabilities"""

        self.SPEC_CAN: dict[tuple[Spec, Capability], bool]
        """whether a class can cover that requirement"""

        self.T = timepoints
        self.TIMEPOINTS = range(self.T)
        self.SPECS = specs
        self.CAPABILITIES = capabilities

        self.SPEC_CAN = {(s, c): 0 for s in self.SPECS for c in self.CAPABILITIES}
        self.SPEC_CAN.update(spec_can)

    @staticmethod
    def from_json(data: dict):
        return Setup(
            timepoints=data.get("timepoints"),
            specs=data.get("specs"),
            capabilities=data.get("capabilities"),
            spec_can=({(a, b): 1 for [a, b] in data.get("spec_can")}),
        )
