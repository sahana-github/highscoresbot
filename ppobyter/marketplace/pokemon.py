from .abilities import abilities


class Pokemon:
    """
    represents a pokemon.
    """
    def __init__(self, happiness, spdef, spatk, speed, defense, atk, hp, spdefev, spatkev, speedev, defev, atkev, hpev,
                 hpiv, atkiv, defiv, spatkiv, spdefiv, speediv, ability, nature, pokemonname, helditem, level, catcher,
                 buildstring):
        ability = int(ability)
        self.buildstring = buildstring
        self.hpiv = hpiv
        self.atkiv = atkiv
        self.defiv = defiv
        self.spatkiv = spatkiv
        self.spdefiv = spdefiv
        self.speediv = speediv
        self.catcher = catcher
        self.ability = abilities.get(ability) if abilities.get(ability) is not None else ability

        self.nature = nature
        self.pokemonname = pokemonname
        self.helditem = helditem
        self.level = level
        self.happiness = happiness
        self.hp = hp
        self.atk = atk
        self.defense = defense
        self.spatk = spatk
        self.spdef = spdef
        self.speed = speed
        self.hpev = hpev
        self.atkev = atkev
        self.defev = defev
        self.spatkev = spatkev
        self.spdefev = spdefev
        self.speedev = speedev

    @staticmethod
    def fromString(string: str):
        try:
            string = string.replace("[", "").replace("]", "")
            splittedstring = string.split(",")

            if len(splittedstring) == 40:
                splittedstring.append("")  # movebank is completely missing if value is absent. normal length 41.

            _, happiness, spdef, spatk, speed, defense, atk, hp, spdefev, spatkev, speedev, defev, atkev, hpev, \
            spdefiv, spatkiv, speediv, defiv, atkiv, hpiv, nature, _, _, _, _, _, _, \
            currenthp, _, _, _, level, pokemonnumber, pokemonname, item, abilitynumber, statusconditionmaybe, _, \
            catcher, _, _ = splittedstring
            builtpoke = Pokemon(happiness=happiness, spdef=spdef, spatk=spatk, speed=speed, defense=defense, atk=atk,
                                hp=hp, spdefev=spdefev, spatkev=spatkev, speedev=speedev, defev=defev, atkev=atkev,
                                hpev=hpev,
                                hpiv=hpiv, atkiv=atkiv, defiv=defiv, spatkiv=spatkiv, spdefiv=spdefiv, speediv=speediv,
                                ability=abilitynumber, nature=nature, pokemonname=pokemonname, helditem=item,
                                level=level, catcher=catcher, buildstring=string)
            return builtpoke
        except Exception as e:

            raise Exception(f"error occured with string: {string} ! {e}")

    def __str__(self):
        return f"""Pokemon properties:
               pokemon name: {self.pokemonname}
               pokemon ability: {self.ability}
               catcher: {self.catcher}
               hp iv: {self.hpiv}
               atk iv: {self.atkiv}
               def iv: {self.defiv}
               sp atk iv: {self.spatkiv}
               sp def iv: {self.spdefiv}
               speediv: {self.speediv}
               level: {self.level}
               held item: {self.helditem}
               nature: {self.nature}
               happiness: {self.happiness}
               hp: {self.hp}
               atk: {self.atk}
               defense: {self.defense}
               spatk: {self.spatk}
               spdef: {self.spdef}
               speed: {self.speed}
               hpev: {self.hpev}
               atkev: {self.atkev}
               defev: {self.defev}
               spatkev: {self.spatkev}
               spdefev: {self.spdefev}
               speedev: {self.speedev}
               buildstring: {self.buildstring}
               """
