import discord
from discord.ext import commands
import music
from flaskserver import live
import os

token = "ODc3NTM3NDI0ODAzMjM3OTY4.YR0EaQ.Vcr0dPUg81B1XBAGEhGgJCWsSqo"
cogs = [music]
intents = discord.Intents().all()
client = commands.Bot(command_prefix='Arif.', intents=intents)


@client.event
async def on_ready():
    print("Bot online")


for i in range(len(cogs)):
    cogs[i].setup(client)

live()
client.run(token)
