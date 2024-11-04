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
        teams: int,
        forbids: list[Timepoint],
    ) -> dict[TeamId, PlannerResult]:
        TEAMS = range(teams)

        solver: Solver = Solver.CreateSolver("SAT")
        if not solver:
            raise "Could not create solver"

        ########
        # VARS #
        ########

        # is this spec gonna be played by this player?
        selected: dict[tuple[PlayerId, Spec, TeamId], bool] = {}
        for t in TEAMS:
            for pid in players:
                for s in setup.SPECS:
                    selected[(pid, s, t)] = solver.BoolVar(f"selected_{pid}_{s}_{t}")

        # will this hour be played by this team?
        playhours: dict[tuple[Timepoint, TeamId], bool] = {}
        for h in setup.TIMEPOINTS:
            for t in TEAMS:
                playhours[(h, t)] = solver.BoolVar(f"playhours_{h}_{t}")

        # is the raid gonna start at this time?
        start: dict[tuple[Timepoint, TeamId], bool] = {}
        for h in setup.TIMEPOINTS:
            for t in TEAMS:
                start[(h, t)] = solver.BoolVar(f"start_{h}_{t}")

        # has this player been chosen to play for this team?
        plays: dict[tuple[PlayerId, Timepoint, TeamId], bool] = {}
        for t in TEAMS:
            for pid in players:
                for h in setup.TIMEPOINTS:
                    plays[(pid, h, t)] = solver.BoolVar(f"plays_{pid}_{h}_{t}")

        #############
        # OBJECTIVE #
        #############

        # non linear function, to skew toward high preferences
        # https://www.desmos.com/calculator/e4zvxwz0xx (curve in green, where M = maxPreference)
        objective: Objective = solver.Objective()
        for t in TEAMS:
            for pid in players:
                for h in setup.TIMEPOINTS:
                    objective.SetCoefficient(
                        plays[(pid, h, t)],
                        (1 - cos(pi * players[pid].preference[h] / maxPreference)) / 2,
                    )
        objective.SetMaximization()

        ###############
        # CONSTRAINTS #
        ###############

        # selected ==> can run
        for pid in players:
            for s in setup.SPECS:
                for t in TEAMS:
                    solver.Add(
                        selected[(pid, s, t)] <= players[pid].specs[(s, raid.id)]
                    )

        # at most one char can be selected for each (player,team)
        for t in TEAMS:
            for pid in players:
                solver.Add(solver.Sum(selected[(pid, s, t)] for s in setup.SPECS) <= 1)

        # each team fulfills all raid requirements
        for t in TEAMS:
            for c in setup.CAPABILITIES:
                covered = solver.Sum(
                    selected[(pid, s, t)] * setup.SPEC_CAN[(s, c)]
                    for pid in players
                    for s in setup.SPECS
                )
                solver.Add(raid.min_requirements[c] <= covered)
                solver.Add(covered <= raid.max_requirements[c])

        # bound teams size
        siz = solver.Sum(
            selected[(pid, s, t)] for t in TEAMS for pid in players for s in setup.SPECS
        )
        solver.Add(raid.min_people <= siz)
        solver.Add(siz <= raid.max_people)

        # starting to play ==> start
        for t in TEAMS:
            for h in setup.TIMEPOINTS:
                # detect change in playhours 0 -> 1, that implies start of play
                solver.Add(
                    playhours[((h + 1) % setup.T, t)] - playhours[(h, t)]
                    <= start[((h + 1) % setup.T, t)]
                )

        # suppress multiple starts
        for t in TEAMS:
            solver.Add(solver.Sum(start[(h, t)] for h in setup.TIMEPOINTS) == 1)

        # suppress plays
        for t in TEAMS:
            for pid in players:
                for h in setup.TIMEPOINTS:
                    # plays_means_has_been_selected
                    solver.Add(
                        plays[(pid, h, t)]
                        <= solver.Sum(selected[(pid, c, t)] for c in setup.SPECS)
                    )
                    # plays_implies_playhours
                    solver.Add(plays[(pid, h, t)] <= playhours[(h, t)])
                    # plays_implies_not_preference_at_0
                    solver.Add(plays[(pid, h, t)] <= players[pid].preference[h])

        # given a timepoint and a player, it can only play in one team
        for h in setup.TIMEPOINTS:
            for pid in players:
                solver.Add(solver.Sum(plays[(pid, h, t)] for t in TEAMS) <= 1)

        # char locked for the week
        for pid in players:
            for s in setup.SPECS:
                solver.Add(solver.Sum(selected[(pid, s, t)] for t in TEAMS) <= 1)

        # limit playtime
        for t in TEAMS:
            solver.Add(
                solver.Sum(playhours[(h, t)] for h in setup.TIMEPOINTS) == raid.length
            )

        # # forbid_times
        # for t in TEAMS:
        #     for f in forbids:
        #         solver.Add(playhours[(f, h)] == 0)

        #######
        # END #
        #######

        status = solver.Solve()

        if status == Solver.OPTIMAL:
            return {
                t: PlannerResult(
                    happiness=solver.Objective().Value(),
                    teamToPlayers=[
                        (pid, s)
                        for pid in players
                        for s in setup.SPECS
                        if selected[(pid, s, t)].solution_value()
                    ],
                    playhours=[
                        h
                        for h in setup.TIMEPOINTS
                        if playhours[(h, t)].solution_value()
                    ],
                    start=[
                        h for h in setup.TIMEPOINTS if start[(h, t)].solution_value()
                    ][0],
                )
                for t in TEAMS
            }
        else:
            return None
