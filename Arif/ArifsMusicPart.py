import datetime

import discord
from discord import Embed
from discord.ext import commands
import music
import Information
import Logs
from flaskserver import live

token = "ODc3NTM3NDI0ODAzMjM3OTY4.YR0EaQ.Vcr0dPUg81B1XBAGEhGgJCWsSqo"
prefix = "Arif."
cogs = [music, Information, Logs]
intents = discord.Intents().all()
client = commands.Bot(command_prefix=prefix, intents=intents)
client.remove_command("help")


@client.event
async def on_ready():
    print("Bot online")




for i in range(len(cogs)):
    cogs[i].setup(client)

live()
client.run(token)
