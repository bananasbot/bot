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
@app_commands.describe(raid="the raid")
@app_commands.describe(timeout="timeout for the calculation")
@app_commands.describe(alternatives="how many alternatives to produce")
@app_commands.choices(
    raid=[raid_to_choice(id, raid) for id, raid in state.raids.items()]
)
async def plan(
    interaction: discord.Interaction,
    raid: str,
    timeout: int = 60,
    alternatives: int = 3,
):
    __logger.info(f"{interaction.user.id} ({interaction.user.name})")

    await interaction.response.defer(thinking=True, ephemeral=True)

    cnt = 0
    forbids = []
    for proposalNo in range(alternatives):
        (res, emb) = await spitOutSolution(
            interaction, proposalNo + 1, forbids, raid, timeout
        )
        if res:
            if cnt == 0:
                await interaction.followup.send(content="I have _some_ proposal.")

            cnt += 1
            await interaction.followup.send(embed=emb)

            forbids += res.playhours
        else:
            # stop if there is no other solution
            if cnt == 0:
                # and if no solution was found, send custom embed
                await interaction.response.edit_message(content=None, embed=emb)
            break

    await interaction.edit_original_response(content=f"I have **{cnt}** proposals(s).")


__logger = logging.getLogger(plan.name)


async def spitOutSolution(
    interaction: discord.Interaction,
    proposalNo: int,
    forbids: list,
    raid: str,
    timeout: int = 60,
) -> tuple[PlannerResult, discord.Embed]:
    planner = asyncio.create_task(
        Planner.plan(
            state.setup,
            state.raids[raid],
            state.players,
            forbids,
        )
    )

    try:
        planned: PlannerResult = await asyncio.wait_for(planner, timeout=timeout)
    except asyncio.TimeoutError:
        planner.cancel()
        await interaction.response.send_message(content="timeout.", ephemeral=True)
        planned = None
        emb = None

    if planned:
        spec_to_players = defaultdict(list[PlayerId])
        for pid, spec in planned.playerToSpec:
            spec_to_players[spec].append(pid)

        t = round(hourToTime(planned.start).timestamp())

        emb = discord.Embed(
            title=f"{state.raids[raid].name}",
            description=f"`Proposal #{proposalNo}`: <t:{t}:F> (<t:{t}:R>)",
            color=Color.brand_green(),
        )
        for spec in spec_to_players:
            emb.add_field(
                name=spec,
                value=" ".join([f"<@{pid}>" for pid in spec_to_players[spec]]),
                inline=False,
            )

    else:
        emb = discord.Embed(
            title=state.raids[raid].name,
            color=Color.dark_red(),
        ).add_field(
            name="No solution",
            value="It could be due to:\n - requirements too strict from Raid\n - too few people ready for that Raid",
            inline=False,
        )

    return (planned, emb)
