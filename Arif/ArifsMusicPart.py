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


@client.command(pass_context=True)
async def help(ctx):
    author=ctx.author
    embed = Embed(title="Message update", description="Message updates", colour=ctx.author.colour,
                  timestamp=datetime.datetime.utcnow())
    embed.set_author(name='Help')
    fields = [("Music", "play,pause,resume,join,disconnect", True),
              ("User", "userinfo or memberinfo,Svinfo or Svinfo", True),
              ("Log", "setupLogChannel or LogChannelSetup  creates log text channel", True)
              ]

    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)
    await  ctx.send(client=author,embed=embed)


for i in range(len(cogs)):
    cogs[i].setup(client)

live()
client.run(token)
