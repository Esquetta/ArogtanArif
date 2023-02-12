import json
import os
import random
import urllib.request
from typing import Optional

import discord
import requests
from discord import Embed
from discord.ext import commands
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
lmt = 15
tenor_key = os.environ.get("TENOR_KEY")
unsplash_key = os.getenv("UNSPLASH_KEY")


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="gif", with_app_command=True,help="Sends gif with specific word you give or random.")
    async def sendGif(self, ctx, *, search_term: Optional[str]):
        search_term = search_term or None
        if search_term is not None:
            r = requests.get("https://g.tenor.com/v1/search?q=%s&key=%s&limit=%s" % (search_term, tenor_key, lmt))
            if r.status_code == 200:
                top_8gifts_first = json.loads(r.content)
                url=str(top_8gifts_first['results'][random.randint(0, 15)]['itemurl'])
                await ctx.send(url,ephemeral=True)
        else:
            word_site = "https://www.mit.edu/~ecprice/wordlist.10000"
            response = urllib.request.urlopen(word_site)
            txt = response.read()
            WORDS = txt.splitlines()
            search_term = random.choice(WORDS)
            r = requests.get("https://g.tenor.com/v1/search?q=%s&key=%s&limit=%s" % (search_term, tenor_key, lmt))
            if r.status_code == 200:
                top_8gifts_first = json.loads(r.content)
                await ctx.send(f"{top_8gifts_first['results'][random.randint(0, 15)]['url']}",ephemeral=True)

    @commands.hybrid_command(name="photo",with_app_command=True,help="Sends photo with specific word you give or random.")
    async def SendPhoto(self, ctx, *, search_term: Optional[str]):
        query = search_term or None
        if query is not None:
            r = requests.get(f"https://api.unsplash.com/search/photos/?query={query}",
                             headers={'Authorization': f'Client-ID {unsplash_key}'})
            if r.status_code == 200:
                image = json.loads(r.content)
                embed = Embed(title="", description="", colour=discord.colour.Color.random())
                embed.set_image(url=image["results"][random.randint(0,len(image["results"])-1)]["urls"]["full"])
                await  ctx.send(embed=embed,ephemeral=True)
        else:
            r = requests.get(f"https://api.unsplash.com/photos/random",
                             headers={'Authorization': f'Client-ID {unsplash_key}'})
            if r.status_code == 200:
                image = json.loads(r.content)
                embed = Embed(title="", description="", colour=discord.colour.Color.random())
                embed.set_image(url=image["urls"]["full"])
                await  ctx.send(embed=embed,ephemeral=True)


async def setup(bot):
   await bot.add_cog(Fun(bot))
