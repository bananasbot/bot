import logging
import asyncio
from collections import defaultdict

import discord
from discord import Color
from discord import app_commands

import state
from models.raid import Raid

from commands.plan.planner import *

from math import ceil


def raid_to_choice(raidId: str, raid: Raid):
    return app_commands.Choice(name=raid.name, value=raidId)


@app_commands.command(
    name="plan",
    description="Helps with finding the best timeslot for the raid.",
)
@app_commands.describe(raid="The raid")
@app_commands.describe(teams="How many teams should I try to build?")
@app_commands.describe(proposals="How many different proposals should I produce?")
@app_commands.describe(timeout="Timeout for the calculation of each proposal")
@app_commands.choices(
    raid=[raid_to_choice(id, raid) for id, raid in state.raids.items()]
)
async def plan(
    interaction: discord.Interaction,
    raid: str,
    teams: int = 2,
    proposals: int = 3,
    timeout: int = 60,
):
    __logger.info(f"{interaction.user.id} ({interaction.user.name})")

    await interaction.response.defer(thinking=True, ephemeral=True)

    cnt = 0
    forbids = []
    for proposalNo in range(proposals):
        (res, embs) = await findSolution(
            interaction, proposalNo + 1, forbids, teams, raid, timeout
        )
        if res:
            if cnt == 0:
                await interaction.followup.send(content="I have _some_ proposal.")

            cnt += 1
            for emb in embs:
                await interaction.followup.send(embed=emb)

            # forbids += res.playhours
        else:
            # stop if there is no other solution
            if cnt == 0:
                # and if no solution was found, send custom embed
                for emb in embs:
                    await interaction.edit_original_response(content=None, embed=emb)
            break

    await interaction.edit_original_response(content=f"I have **{cnt}** proposals(s).")


__logger = logging.getLogger(plan.name)


async def findSolution(
    interaction: discord.Interaction,
    proposalNo: int,
    forbids: list,
    teams: int,
    raid: str,
    timeout: int = 60,
) -> tuple[PlannerResult, None | list[discord.Embed]]:
    planner = asyncio.create_task(
        Planner.plan(
            state.setup,
            state.raids[raid],
            state.players,
            teams,
            forbids,
        )
    )

    try:
        planned: dict[TeamId, PlannerResult] = await asyncio.wait_for(
            planner,
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        planner.cancel()
        await interaction.response.send_message(content="timeout.", ephemeral=True)
        planned = None
        embs = None

    if planned:
        embs = []
        for tid in planned:
            spec_to_players = defaultdict(list[PlayerId])

            for pid, spec in planned[tid].teamToPlayers:
                spec_to_players[spec].append(pid)

            t = round(hourToTime(planned[tid].start).timestamp())
            emb = discord.Embed(
                title=f"{state.raids[raid].name} (Proposal #{proposalNo})",
                description=f"Team `{tid + 1}`: <t:{t}:F> (<t:{t}:R>)",
                color=Color.brand_green(),
            )
            for spec in spec_to_players:
                emb.add_field(
                    name=spec,
                    value=" ".join([f"<@{pid}>" for pid in spec_to_players[spec]]),
                    inline=False,
                )

            embs.append(emb)

    else:
        emb = discord.Embed(
            title=state.raids[raid].name,
            color=Color.dark_red(),
        ).add_field(
            name="No solution",
            value=__unsat_message,
            inline=False,
        )
        embs = [emb]

    return (planned, embs)


__unsat_message = """
This could be due to:
- requirements too strict from Raid
- too few people ready for that Raid
- too many teams to satisfy the constraints above"""
