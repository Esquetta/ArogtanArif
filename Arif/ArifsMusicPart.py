import asyncio
import openai
import discord
from discord.ext import commands
import Chat
from discord import app_commands
import Fun
import music
import Information
from typing import Literal, Union, NamedTuple
# import Logs
import Game
from flaskserver import live
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
token = os.getenv('DISCORD_TOKEN')
openai.api_key = os.getenv('OPENAI_API_KEY')
prefix = "Arif."
OWNER_IDS = [276761363022479361]
cogs = [music, Information, Game, Fun, Chat]
intents = discord.Intents().all()
client = commands.Bot(command_prefix=prefix, intents=intents, owner_ids=OWNER_IDS)
client.remove_command("help")


@client.event
async def on_ready():
    print("Bot online")
    synec = await  client.tree.sync()
    print(f"{len(synec)} command  synced.")


@client.tree.command(name="first")
async def first_command(interaction: discord.Interaction):
    await interaction.response.send_message("Hello!", ephemeral=True)


async def main():
    async with client:
        for i in range(len(cogs)):
            await cogs[i].setup(client)
        await client.start(token)


asyncio.run(main())
live()
