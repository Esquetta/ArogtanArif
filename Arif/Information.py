import datetime
from typing import Optional
import discord
from discord import Member
from discord.ext import commands


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="userinfo",help="Show specifieded user info. ",aliases=["memberinfo"])
    async def user_info(self, ctx, user: Optional[Member]):
        user = user or ctx.author
        embedInfo = discord.Embed(title="User Information", colour=user.guild.owner.colour,
                                  timestamp=datetime.datetime.utcnow())
        embedInfo.set_thumbnail(url=user.avatar_url)
        embedInfo.set_thumbnail(url=ctx.guild.icon_url)
        fields = [("ID", user.id, False),
                  ("Username", str(user), True),
                  ("Is Bot ?", user.bot, True),
                  ("Created At", user.created_at, True),
                  ("Status", str(user.status).title(), True),
                  ("joined at", user.joined_at.strftime("%d.%m.%Y %H:%M:%S"), True),
                  ("Activity",
                   f"{str(user.activity.type).split('.')[-1].title() if user.activity else ''} {user.activity.name if user.activity else 'N/A'}",
                   True),
                  ("Boosted ?", bool(user.premium_since), True),
                  ("Top Role", user.top_role.mention, True)]

        for name, value, inline in fields:
            embedInfo.add_field(name=name, value=value, inline=inline)

        await  ctx.send(embed=embedInfo)

    @commands.command(name="SvInfo", help="Shows server info.", aliases=["svinfo"])
    async def server_info(self, ctx):
        embed = discord.Embed(title="Server Information", colour=ctx.guild.owner.colour,
                              timestamp=datetime.datetime.utcnow())
        statuses = [len(list(filter(lambda m: str(m.status) == "online", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "idle", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "dnd", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "offline", ctx.guild.members)))
                    ]
        fields = [("ID", ctx.guild.id, True),
                  ("Name",ctx.guild.name,True),
                  ("Owner", ctx.guild.owner, True),
                  ("Region", ctx.guild.region, True),
                  ("Created at", ctx.guild.created_at.strftime("%d.%m.%Y %H:%M:%S"), True),
                  ("Members", len(ctx.guild.members), True),
                  ("Humans", len(list(filter(lambda m: not m.bot, ctx.guild.members))), True),
                  ("Bots", len(list(filter(lambda m:m.bot, ctx.guild.members))), True),
                  ("Banned Users", len(await ctx.guild.bans()), True),
                  ("Statuses",
                   f":green_circle: {statuses[0]} :orange_circle:{statuses[1]} :red_circle:{statuses[2]} :white_circle:{statuses[3]}",
                   True),
                  ("Text Channels", len(ctx.guild.text_channels), True),
                  ("Voice Channels", len(ctx.guild.voice_channels), True),
                  ("Roles Count", len(ctx.guild.roles), True),
                  ("Categories", len(ctx.guild.categories), True),
                  ("Invites", len(await ctx.guild.invites()), True),
                  ("\u200b","\u200b",True)
                  ]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.add_field(name="Roles",value=",@".join([str(i.name) for i in ctx.guild.roles]))
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Information(client))
