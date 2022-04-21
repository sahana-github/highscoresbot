from discord import Interaction, app_commands


async def worldbosspokemonautocomplete(interaction: Interaction, current: str):
    current = current.lower()
    pokemons = ['articuno', 'azelf', 'cresselia', 'darkrai', 'entei',
                'giratina', 'heatran', 'latias', 'latios', 'mesprit', 'mew',
                'moltres', 'raikou', 'regigigas', 'shaymin', 'suicune', 'uxie',
                'yveltal', 'zapdos']
    suggestions = []
    for pokemon in pokemons:
        if current in pokemon:
            suggestions.append(pokemon)
        if len(suggestions) == 25:
            break
    return [app_commands.Choice(name=pokemon, value=pokemon) for pokemon in suggestions]


async def worldbosslocationautocomplete(interaction: Interaction, current: str):
    current = current.lower()
    locations = ["deep viridian forest", "deep viridian forest 2", "power plant", "diglett's cave",
                  "route 11", "route 12", "route 13", "route 14", "route 15", "route 16", "route 17",
                  "route 18", "mt ember", "berry forest", "route 23",  # end kanto
                  "route 26", "route 27", "route 29", "route 30", "route 31", "route 32", "route 33",
                  "route 34", "ilex forest", "route 35", "national park", "route 36", "route 37",
                  "route 38", "route 39", "route 42", "route 43", "route 44", "mossy cave", "route 45",
                  "route 46", "route 48",  # end johto
                  "route 28", "route 101", "route 102", "route 103", "route 104", "route 110", "route 111",
                  "route 112", "route 113", "route 114", "route 115", "route 116", "rusturf tunnel",
                  "route 117", "route 118", "route 119", "route 120", "route 121", "route 123",  # end hoenn
                  "route 201", "route 202", "route 203", "route 204", "route 205", "route 206", "route 207",
                  "route 208", "route 209", "route 210 a", "route 210 b", "route 211", "route 212 a",
                  "route 212 b", "route 224"  # end sinnoh
                  ]
    suggestions = []
    for location in locations:
        if current in location:
            suggestions.append(location)
        if len(suggestions) == 25:
            break
    return [app_commands.Choice(name=location, value=location) for location in suggestions]