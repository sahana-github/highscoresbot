from discord import app_commands, Interaction

from commands.utils.utils import gettournamentprizes


async def tournamentprizeautocomplete(interaction: Interaction, current: str):
    current = current.lower()
    tournamentprizes = gettournamentprizes()
    suggestions = []
    for tournamentprize in tournamentprizes:
        if current in tournamentprize:
            suggestions.append(tournamentprize)
        if len(suggestions) == 25:
            break
    return [app_commands.Choice(name=tournamentprize, value=tournamentprize) for tournamentprize in suggestions]


async def tournamenttypeautocomplete(interaction: Interaction, current: str):
    return [app_commands.Choice(name=i, value=i)
            for i in ["ubers", "self caught", "little cup", "monotype", "set level 100"]]