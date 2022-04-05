from discord import Interaction
from discord import app_commands
from commands.utils.utils import getswarmpokemons, getswarmlocations


async def swarmpokemonautocomplete(interaction: Interaction, current: str):
    current = current.lower()
    pokemons = getswarmpokemons()
    suggestions = []
    for pokemon in pokemons:
        if current in pokemon:
            suggestions.append(pokemon)
        if len(suggestions) == 25:
            break
    return [app_commands.Choice(name=pokemon, value=pokemon) for pokemon in suggestions]


async def swarmlocationautocomplete(interaction: Interaction, current: str):
    current = current.lower()
    locations = getswarmlocations()
    suggestions = []
    for location in locations:
        if current in location:
            suggestions.append(location)
        if len(suggestions) == 25:
            break
    return [app_commands.Choice(name=location, value=location) for location in suggestions]