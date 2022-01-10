import json
import os
import random
import urllib.request
from typing import Optional

import requests
from discord.ext import commands

lmt = 15
tenor_key = os.getenv("TENOR_KEY")


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="Gif", aliases=["gif"])
    async def sendGif(self, ctx, *, search_term: Optional[str]):
        search_term = search_term or ""
        if search_term is not None:
            r = requests.get("https://g.tenor.com/v1/search?q=%s&key=%s&limit=%s" % (search_term, tenor_key, lmt))
            if r.status_code == 200:
                top_8gifts_first = json.loads(r.content)
                await ctx.send(f"{top_8gifts_first['results'][random.randint(0, 15)]['url']}")
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


def setup(client):
    client.add_cog(Fun(client))