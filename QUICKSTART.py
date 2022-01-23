"""
This file is to create all the databases needed to run the bot.
"""


from quickstart.database_build import DatabaseBuild
import os
import sqlite3
from quickstart.functionality_check import FunctionalityCheck


if __name__ == "__main__":
    # making sure the files exist if they do not.
    print("starting setup for the highscores bot.")
    sqlite3.connect("highscores.db").close()
    sqlite3.connect("data.db").close()
    sqlite3.connect("eventconfigurations.db").close()
    sqlite3.connect("ingame_data.db").close()
    try:
        os.remove("paths.json")
    except FileNotFoundError:
        pass
    dbbuild = DatabaseBuild()
    dbbuild.highscoresDatabase()
    dbbuild.ingame_data()
    dbbuild.eventconfiguration()
    dbbuild.data()
    print("setup complete. Verifying database.")
    functionalityCheck = FunctionalityCheck()
    while not (check := functionalityCheck.checkHighscoreFunctionality()):
        if check.hasFix():
            result = input(str(check) + " Proceed with auto fix? Y/n")
            if result.lower() == "n":
                break
            else:
                print("proceeding with auto fix.")
                check.fix()
        else:
            print(str(check), "no auto fix available. Please try removing the database(s) and try quickstart again.")
            break
    print("verifying complete.")
    print("making worldbosstime.txt")
    with open("worldbosstime.txt", "w") as file:
        file.write("1\n1638109422")
    print("worldbosstime.txt made.")
