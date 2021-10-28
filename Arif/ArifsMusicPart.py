import discord
from discord.ext import commands
import music
from flaskserver import  live
import os

#TOKEN=os.getenv("discord_token")
token="ODc3NTM3NDI0ODAzMjM3OTY4.YR0EaQ.Vcr0dPUg81B1XBAGEhGgJCWsSqo"
cogs = [music]
intents=discord.Intents().all()
client = commands.Bot(command_prefix='Arif.', intents=intents)




for i in range(len(cogs)):
    cogs[i].setup(client)


live()
client.run(token)