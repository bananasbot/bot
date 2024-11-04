from ortools.init.python import init
from ortools.linear_solver.pywraplp import Objective, Solver

from math import cos, pi

from models.player import Player
from models.raid import Raid
from models.setup import *

from commands.plan.plannerResult import PlannerResult


class Planner:
    """The actual planner"""

    async def plan(
        setup: Setup,
        raid: Raid,
        players: dict[int, Player],
        forbids: list[Timepoint],
    ) -> PlannerResult:
        solver: Solver = Solver.CreateSolver("SAT")
        if not solver:
            raise "Could not create solver"

        ########
        # VARS #
        ########

        # is this spec gonna be played by this player?
        selected: dict[(PlayerId, Spec), bool] = {}
        for pid in players:
            for s in setup.SPECS:
                selected[(pid, s)] = solver.BoolVar(f"selected_{pid}_{s}")

        # will this hour be played?
        playhours: dict[Timepoint, bool] = {}
        for h in setup.TIMEPOINTS:
            playhours[h] = solver.BoolVar(f"playhours_{h}")

        # is the raid gonna start at this time?
        start: dict[Timepoint, bool] = {}
        for h in setup.TIMEPOINTS:
            start[h] = solver.BoolVar(f"start_{h}")

        # has this player been chosen to play?
        plays: dict[(PlayerId, Timepoint), bool] = {}
        for pid in players:
            for h in setup.TIMEPOINTS:
                plays[(pid, h)] = solver.BoolVar(f"plays_{pid}_{h}")

        #############
        # OBJECTIVE #
        #############

        # non linear function, to skew toward high preferences
        # https://www.desmos.com/calculator/e4zvxwz0xx (curve in green, where M = maxPreference)
        objective: Objective = solver.Objective()
        for pid in players:
            for h in setup.TIMEPOINTS:
                objective.SetCoefficient(
                    plays[(pid, h)],
                    (1 - cos(pi * players[pid].preference[h] / maxPreference)) / 2,
                )
        objective.SetMaximization()

        ###############
        # CONSTRAINTS #
        ###############

        # select_implies_can_run
        for pid in players:
            for s in setup.SPECS:
                solver.Add(selected[(pid, s)] <= players[pid].specs[(s, raid.id)])

        # at_most_one_char_per_player_selected
        for pid in players:
            solver.Add(solver.Sum(selected[(pid, s)] for s in setup.SPECS) <= 1)

        # fulfill_all_raid_requirements
        for c in setup.CAPABILITIES:
            s = solver.Sum(
                selected[(pid, s)] * setup.SPEC_CAN[(s, c)]
                for pid in players
                for s in setup.SPECS
            )
            solver.Add(raid.min_requirements[c] <= s)
            solver.Add(s <= raid.max_requirements[c])

        # people amount bounds
        p = solver.Sum(selected[(pid, s)] for pid in players for s in setup.SPECS)
        solver.Add(raid.min_people <= p)
        solver.Add(p <= raid.max_people)

        # single_start_1
        for h in setup.TIMEPOINTS:
            solver.Add(
                playhours[(h + 1) % setup.T] - playhours[h] <= start[(h + 1) % setup.T]
            )

        # single_start_2
        solver.Add(solver.Sum(start[h] for h in setup.TIMEPOINTS) == 1)

        # suppress_play
        for pid in players:
            for h in setup.TIMEPOINTS:
                # plays_means_has_been_selected
                solver.Add(
                    plays[(pid, h)]
                    <= solver.Sum(selected[(pid, c)] for c in setup.SPECS)
                )
                # plays_implies_playhours
                solver.Add(plays[(pid, h)] <= playhours[h])
                # plays_implies_not_preference_at_0
                solver.Add(plays[(pid, h)] <= players[pid].preference[h])

        # limit playtime
        solver.Add(solver.Sum(playhours[h] for h in setup.TIMEPOINTS) == raid.length)

        # forbid_times
        for f in forbids:
            solver.Add(playhours[f] == 0)

        #######
        # END #
        #######

        status = solver.Solve()

        if status == Solver.OPTIMAL:
            pids = [
                (pid, s)
                for s in setup.SPECS
                for pid in players
                if selected[(pid, s)].solution_value()
            ]
            playhs = [h for h in setup.TIMEPOINTS if playhours[h].solution_value()]
            st = [h for h in setup.TIMEPOINTS if start[h].solution_value()]

            return PlannerResult(solver.Objective().Value(), pids, playhs, st[0])
        else:
            return []
