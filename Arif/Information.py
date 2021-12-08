import datetime
from typing import Optional
import discord
from discord import Member
from discord.ext import commands

class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="userinfo", aliales=["memberinfo"])
    async def user_info(self, ctx,user:Optional[Member]):
        user = user or ctx.author
        embedInfo = discord.Embed(title="User Information", colour=user.guild.owner.colour, timestamp=datetime.datetime.utcnow())
        embedInfo.set_thumbnail(url=user.avatar_url)
        embedInfo.set_thumbnail(url=ctx.guild.icon_url)
        fields = [("ID", user.id, False),
                  ("Username", str(user), True),
                  ("Is Bot ?", user.bot, True),
                  ("Created At", user.created_at,True),
                  ("Status", str(user.status).title(), True),
                  ("joined at", user.joined_at.strftime("%d.%m.%Y %H:%M:%S"), True),
                  ("Activity", f"{str(user.activity.type).split('.')[-1].title() if user.activity else ''} {user.activity.name if user.activity else 'N/A'}", True),
                  ("Boosted ?",bool(user.premium_since),True),
                  ("Top Role", user.top_role.mention, True)]

        for name, value, inline in fields:
            embedInfo.add_field(name=name, value=value, inline=inline)

        await  ctx.send(embed=embedInfo)

def setup(client):
    client.add_cog(Information(client))
