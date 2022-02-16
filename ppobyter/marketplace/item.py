import json
from typing import Union

from ppobyter.marketplace.pokemon import Pokemon


class Item:
    """
    Represents an item in gm.
    """
    def __init__(self, itemname: str, sellid, seller, price, amount, intention="sell",
                 pokemon: Union[Pokemon, None] = None):
        """

        :param itemname: name of the item
        :param sellid: id of the sell in global market
        :param seller: name of the seller
        :param price: the price of the item
        :param amount: amount of the item for the price.
        :param intention: selling, auction etc.
        :param pokemon: if the item is a pokemon this is the pokemon.
        """
        self.itemname = itemname
        self.sellid = sellid
        self.seller = seller
        self.price = price
        self.amount = amount
        self.intention = intention
        self.pokemon = pokemon

    def isPokemon(self):
        return self.pokemon is not None

    def __str__(self):
        print(f"is pokemon: {self.isPokemon()}")
        return f"""
sellid: {self.sellid}
name item: {self.itemname}
amount: {self.amount}
price: {self.price}
seller: {self.seller}        

{str(self.pokemon) if self.isPokemon() else ""}
"""

    def to_dict(self):
        asdict = {"sellid": self.sellid,
                "name": self.itemname,
                "amount": self.amount,
                "price": self.price,
                "seller": self.seller
         }
        if self.isPokemon():
            asdict["pokemon"] = self.pokemon.to_dict()
        return asdict

    @staticmethod
    def from_dict(jsondata: dict):
        pokemon = None
        if "pokemon" in jsondata:
            pokemon = Pokemon.from_dict(jsondata["pokemon"])
        return Item(jsondata["name"], jsondata["sellid"], jsondata["seller"], jsondata["price"], jsondata["amount"],
                    "sell", pokemon)
