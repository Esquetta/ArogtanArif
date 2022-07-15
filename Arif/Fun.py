import json
import os
import random
import urllib.request
from typing import Optional

import discord
import requests
from discord.ext import commands
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
lmt = 15
tenor_key = os.environ.get("TENOR_KEY")
unsplash_key = os.getenv("UNSPLASH_KEY")


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="Gif", aliases=["gif"])
    async def sendGif(self, ctx, *, search_term: Optional[str]):
        search_term = search_term or None
        if search_term is not None:
            r = requests.get("https://g.tenor.com/v1/search?q=%s&key=%s&limit=%s" % (search_term, tenor_key, lmt))
            if r.status_code == 200:
                top_8gifts_first = json.loads(r.content)
                url=str(top_8gifts_first['results'][random.randint(0, 15)]['url'])
                embed = discord.Embed(title="",description="",colour=discord.colour.Color.random())
                embed.set_image(url=url)
                await ctx.send(embed=embed)
                await ctx.send(url)
        else:
            word_site = "https://www.mit.edu/~ecprice/wordlist.10000"
            response = urllib.request.urlopen(word_site)
            txt = response.read()
            WORDS = txt.splitlines()
            search_term = random.choice(WORDS)
            r = requests.get("https://g.tenor.com/v1/search?q=%s&key=%s&limit=%s" % (search_term, tenor_key, lmt))
            if r.status_code == 200:
                top_8gifts_first = json.loads(r.content)
                await ctx.send(f"{top_8gifts_first['results'][random.randint(0, 15)]['url']}")

    @commands.command(name="Photo", aliases=["photo"])
    async def SendPhoto(self, ctx, *, filter: Optional[str]):
        query = filter or ""
        if query is not None:
            r = requests.get(f"https://api.unsplash.com/search/photos/?query={query}",
                             headers={'Authorization': f'Client-ID {unsplash_key}'})
            if r.status_code == 200:
                image = json.loads(r.content)
                await  ctx.send(image)


def setup(client):
    client.add_cog(Fun(client))
