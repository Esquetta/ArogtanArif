import datetime
from typing import Optional
import discord
from discord import Member, Embed
from discord.ext import commands


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="Userinfo", help="Show specified user info. ", aliases=["MemberInfo", "userinfo"])
    async def user_info(self, ctx, user: Optional[Member]):
        user = user or ctx.author
        embedInfo = discord.Embed(title="User Information", colour=user.guild.owner.colour,
                                  timestamp=datetime.datetime.utcnow())
        embedInfo.set_thumbnail(url=user.avatar_url)

        fields = [("ID", user.id, False),
                  ("Username", str(user.mention), True),
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
        embed.set_thumbnail(url=ctx.guild.icon_url)
        statuses = [len(list(filter(lambda m: str(m.status) == "online", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "idle", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "dnd", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "offline", ctx.guild.members)))
                    ]
        fields = [("ID", ctx.guild.id, True),
                  ("Name", ctx.guild.name, True),
                  ("Owner", ctx.guild.owner.mention, True),
                  ("Region", ctx.guild.region, True),
                  ("Created at", ctx.guild.created_at.strftime("%d.%m.%Y %H:%M:%S"), True),
                  ("Members", len(ctx.guild.members), True),
                  ("Humans", len(list(filter(lambda m: not m.bot, ctx.guild.members))), True),
                  ("Bots", len(list(filter(lambda m: m.bot, ctx.guild.members))), True),
                  ("Banned Users", len(await ctx.guild.bans()), True),
                  ("Statuses",
                   f":green_circle: {statuses[0]} :orange_circle:{statuses[1]} :red_circle:{statuses[2]} :white_circle:{statuses[3]}",
                   True),
                  ("Text Channels", len(ctx.guild.text_channels), True),
                  ("Voice Channels", len(ctx.guild.voice_channels), True),
                  ("Roles Count", len(ctx.guild.roles), True),
                  ("Categories", len(ctx.guild.categories), True),
                  ("Invites", len(await ctx.guild.invites()), True),
                  ("\u200b", "\u200b", True)
                  ]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.add_field(name="Roles", value=",@".join([str(i.name) for i in ctx.guild.roles]))
        await ctx.send(embed=embed)

    @commands.command(name="avatar", aliases=["Avatar"])
    async def avatar(self, ctx, user: Optional[Member]):
        user = user or ctx.author
        embed = Embed(title=f"Avatar For {user.name}", colour=user.guild.owner.colour,
                      timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Links",
                        value=f"[png]({user.avatar_url_as(format=None, static_format='png')}),[jpeg]({user.avatar_url_as(format=None, static_format='jpeg')}),[webp]({user.avatar_url_as(format=None, static_format='webp')})",
                        inline=True)
        embed.set_image(url=user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name="roleinfo", aliases=["roleInfo,RoleInfo,Roleinfo"])
    async def role_info(self, ctx, *, role: Optional[str]):
        role = role or ctx.author.top_role
        embed = Embed(title="Role Information", colour=role.colour, timestamp=datetime.datetime.utcnow())
        fields = [("ID", role.id, True), ("Name", role.name, True), ("Color", role.color, True),
                  ("Hoisted", role.hoist, True), ("Mentionable", role.mentionable, True),
                  ("Role Created", role.created_at.strftime("%d.%m.%Y %H:%M:%S"), True),
                  ("Position (from top)", f"({role.position}/{len(ctx.guild.roles)})", True),
                  ("Permissions",f"{''.join([i[0] for i in role.permissions])}", True)]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    async def help(self, ctx):
        embed = Embed(title="Commands ", description="Arif Commands List ", colour=ctx.author.colour,
                      timestamp=datetime.datetime.utcnow())
        embed.set_author(name='Help')
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        fields = [("Music", "play,pause,resume,join,disconnect,nowplaying,skip,loop", True),
                  ("User", "userinfo or memberinfo,Svinfo or Svinfo", True),
                  ("Log", "setupLogChannel or LogChannelSetup  creates log text channel", True),
                  ("Game", "Rock-Paper-Scissors,CoinFlip", "True"),
                  ("Fun", "Gif", "True"),
                  ("More", "Arif.help 'command name' extented help with specified command.", "True")

                  ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        await  ctx.send(embed=embed)

    @help.command(name="play")
    async def play(self, ctx):
        embed = Embed(title="Play", description="Play usage", colour=ctx.author.colour,
                      timestamp=datetime.datetime.utcnow())
        embed.set_author(name="Play")
        embed.add_field(name="Exp", value="Arif.play or Arif.sing 'youtube link'", inline=True)
        await  ctx.send(embed=embed)

    @help.command(name="pause")
    async def pause(self, ctx):
        embed = Embed(title="Pause", description="Pause usage", colour=ctx.author.colour,
                      timestamp=datetime.datetime.utcnow())
        embed.set_author(name="Pause")
        embed.add_field(name="Exp", value="Arif.pause or Arif.stop", inline=True)
        embed.add_field(name="Return", value="Bot returns message if music paused successfully.", inline=True)
        await  ctx.send(embed=embed)

    @help.command(name="resume")
    async def resume(self, ctx):
        embed = Embed(title="Resume", description="Resume usage", colour=ctx.author.colour,
                      timestamp=datetime.datetime.utcnow())
        embed.set_author(name="Resume")
        embed.add_field(name="Exp", value="Arif.resume", inline=True)
        embed.add_field(name="Return", value="Bot returns message if music resumed successfully.", inline=True)
        await  ctx.send(embed=embed)

    @help.command(name="disconnect")
    async def disconnect(self, ctx):
        embed = Embed(title="disconnect", description="Disconnect usage", colour=ctx.author.colour,
                      timestamp=datetime.datetime.utcnow())
        embed.set_author(name="Disconnect")
        embed.add_field(name="Exp", value="Arif.disconnect or Arif.leave", inline=True)
        embed.add_field(name="Return", value="Bot leaves from voice channel.", inline=True)
        await  ctx.send(embed=embed)

    @help.command(name="userinfo")
    async def user_Info(self, ctx):
        embed = Embed(title="userinfo", description="userinfo usage", colour=ctx.author.colour,
                      timestamp=datetime.datetime.utcnow())
        embed.set_author(name="Disconnect")
        embed.add_field(name="Exp", value="Arif.userinfo or Arif.memberinfo", inline=True)
        embed.add_field(name="Return", value="If you dont give a user (Arif.userinfo) return your account information.",
                        inline=True)
        embed.add_field(name="Return",
                        value="If you dont give a user (Arif.userinfo @Me) return specified user  account information.",
                        inline=True)
        await  ctx.send(embed=embed)

    @help.command(name="SvInfo")
    async def sv_Info(self, ctx):
        embed = Embed(title="SvInfo", description="svinfo usage", colour=ctx.author.colour,
                      timestamp=datetime.datetime.utcnow())
        embed.set_author(name="SvInfo")
        embed.add_field(name="Exp", value="Arif.SvInfo or Arif.vInfo", inline=True)
        embed.add_field(name="Return", value="If you dont give a user (Arif.SvInfo) return your server information.",
                        inline=True)
        await  ctx.send(embed=embed)

    @help.command(name="setupLogChannel")
    async def setupLogChannel(self, ctx):
        embed = Embed(title="setupLogChannel", description="setupLogChannel usage", colour=ctx.author.colour,
                      timestamp=datetime.datetime.utcnow())
        embed.set_author(name="Disconnect")
        embed.add_field(name="Exp", value="Arif.SvInfo or Arif.vInfo", inline=True)
        embed.add_field(name="Info",
                        value="Arif creates named log channel and userprofle,username,message edit,message delete all this triggered sends log channel.(Everyone can see and write this channel)",
                        inline=True)
        await  ctx.send(embed=embed)

    @help.command(name="RockPaperScissors")
    async def RockPaperScissor(self, ctx):
        embed = Embed(title="Rock-Paper-Scissors", description="Rock-Paper-Scissors usage", colour=ctx.author.colour,
                      timestamp=datetime.datetime.utcnow())
        embed.set_author(name="Game")
        embed.add_field(name="Exp", value="Arif.RockPaperScissors", inline=True)
        embed.add_field(name="Info",
                        value="Arif.RockPaperScissors 'and your choice' after bot return his choice and who is winner.",
                        inline=True)
        await  ctx.send(embed=embed)


def setup(client):
    client.add_cog(Information(client))
