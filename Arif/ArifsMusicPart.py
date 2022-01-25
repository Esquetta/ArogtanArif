import asyncio
import random

import discord
from discord.ext import commands

import Fun
import music
import Information
import Logs
import Game
from flaskserver import live
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
prefix = "Arif."
OWNER_IDS = [276761363022479361]
cogs = [music, Information, Logs, Game, Fun]
intents = discord.Intents().all()
client = commands.Bot(command_prefix=prefix, intents=intents, owner_ids=OWNER_IDS)
client.remove_command("help")


@client.event
async def on_ready():
    print("Bot online")


for i in range(len(cogs)):
    cogs[i].setup(client)

live()
client.run(token)
