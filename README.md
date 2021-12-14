This is the github repository of the highscores bot for the game pokemon planet.

To run this bot, follow the following steps.

<ol>
<li>Run QUICKSTART.py in this folder to create all needed databases.</li>
<li><p>Add "username" to environment variables, with as value the name of a pokemon planet account.
<p>Also add "password" to environment variables, with as value the password for the pokemon planet account.</p>
Note this can be any account, as long as it can log in to the pokemon planet website.</p>
<p>It is recommended to run HighscoresUpdater.updateHighscores at least once. For the actual bot highscoresupdater.py is run constantly.</p></li>
<li>Add "token" to environment variables, with as value a discord token. After that you can run main.py in the same folder as this readme file.</li>
<li><p>(this step is not required if you don't want to run eventannouncements) 
<p>To run the eventannouncement part, you'll need to run main.py inside the ppobyter folder. Then you'll need to log in to the downloadeable client of pokemon planet.</p>
Note that you might need to adjust the interface (where self.__cap is made) in ppobyter/main.py, to where the pokemon planet traffic goes through.
</li>
</ol>

This discord bot uses the following requirements, these include but are not limited to:
<ul>
<li>python 3.9+</li>
<li>discord.py</li>
<li>pyshark</li>
<li>nest_asyncio</li>
<li>asyncio</li>
<li>discord_components</li>
<li>typing</li>
<li>sqlite3</li>
</ul>
If you have any questions, feel free to pm kevin123456#2069 on discord.