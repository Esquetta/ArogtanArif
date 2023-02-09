import datetime
from typing import Optional
import discord
from discord import Member, Embed
from discord.ext import commands
from discord import app_commands


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="Userinfo", help="Show specified user info. ", aliases=["MemberInfo", "userinfo"])
    async def user_info(self, ctx, user: Optional[Member]):
        user = user or ctx.author
        embedInfo = discord.Embed(title="User Information", colour=user.guild.owner.colour,
                                  timestamp=datetime.datetime.utcnow())
        embedInfo.set_thumbnail(url=user.avatar)

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

    @commands.command(name="Ping", aliases=["ping"])
    async def ping(self, ctx):
        await ctx.send(f"Pong! {round(ctx.bot.latency * 1000)}ms")

    @commands.command(name="SvInfo", help="Shows server info.", aliases=["svinfo"])
    async def server_info(self, ctx):
        embed = discord.Embed(title="Server Information", colour=ctx.guild.owner.colour,
                              timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=ctx.guild.icon.url)
        statuses = [len(list(filter(lambda m: str(m.status) == "online", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "idle", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "dnd", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "offline", ctx.guild.members)))
                    ]
        fields = [("ID", ctx.guild.id, True),
                  ("Name", ctx.guild.name, True),
                  ("Owner", ctx.guild.owner.mention, True),
                  ("Created at", ctx.guild.created_at.strftime("%d.%m.%Y %H:%M:%S"), True),
                  ("Members", ctx.guild.member_count, True),
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
                        value=f"[png]({user.avatar.with_static_format('png')}),[jpeg]({user.avatar.with_static_format('jpeg')}),[webp]({user.avatar.with_static_format('webp')})",
                        inline=True)
        embed.set_image(url=user.avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="roleinfo", aliases=["roleInfo,RoleInfo,Roleinfo"])
    async def role_info(self, ctx, *, role: Optional[str]):
        role = role or ctx.author.top_role
        permissions = []
        for i in role.permissions:
            item = " ".join(i[0].split('_'))
            permissions.append(f"**`{item.capitalize()}`**'")
        embed = Embed(title="Role Information", colour=role.colour, timestamp=datetime.datetime.utcnow())
        fields = [("ID", role.id, True), ("Name", role.name, True), ("Color", role.color, True),
                  ("Hoisted", role.hoist, True), ("Mentionable", role.mentionable, True),
                  ("Role Created", role.created_at.strftime("%d.%m.%Y %H:%M:%S"), True),
                  ("Position (from top)", f"({role.position}/{len(ctx.guild.roles)})", True),
                  ("Permissions", f"{''.join([i for i in permissions])}", True)]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        await ctx.send(embed=embed)

    @commands.group(name="help", aliases=["Help"], invoke_without_command=True)
    async def help(self, ctx):
        embed = Embed(title="Commands ", description="Arif Commands List ", colour=ctx.author.colour,
                      timestamp=datetime.datetime.utcnow())
        embed.set_author(name='Help')
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        fields = [("Music:musical_note: ",
                   "play,pause,resume,join,disconnect,nowplaying,skip,loop,lyrics,shuffle,playlist,removequeue,lyrics",
                   "True"),
                  ("Info:information_source:", "userinfo,Svinfo,avatar,roleinfo,ping", "True"),
                  ("Log:pencil: ", "setupLogChannel or LogChannelSetup  creates log text channel", "True"),
                  ("Game:game_die: ", "Rock-Paper-Scissors,CoinFlip,NumberGuess,Bigtext,CoinFlip", "True"),
                  ("Fun:tada:", "Gif", "Photo", "True"),
                  ("More", "Arif.help 'command name' extented help with specified command.", "True")

                  ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        await  ctx.send(embed=embed)

    @help.command(name="play")
    async def play(self, ctx):
        embed = Embed(description="Plays a song", colour=ctx.author.colour,
                      timestamp=datetime.datetime.utcnow())
        embed.set_author(name="Play")
        embed.add_field(name="Usage", value="**`Arif.play 'youtube link' or name of song `**", inline=True)
        embed.add_field(name="Aliases", value="**`Sing,p`**", inline=True)
        embed.add_field(name="Example", value="**`Arif.play logic ballin`** ", inline=True)

        await  ctx.send(embed=embed)

    @help.command(name="pause")
    async def pause(self, ctx):
        embed = Embed(description="**`Bot returns message if music paused successfully.`**", colour=ctx.author.colour,
                      timestamp=datetime.datetime.utcnow())
        embed.set_author(name="Pause")
        embed.add_field(name="Exp", value="**`Arif.pause`**", inline=True)
        await  ctx.send(embed=embed)

    @help.command(name="resume")
    async def resume(self, ctx):
        embed = Embed(description="**`Bot returns message if music resumed successfully.`**", colour=ctx.author.colour,
                      timestamp=datetime.datetime.utcnow())
        embed.set_author(name="Resume")
        embed.add_field(name="Exp", value="Arif.resume", inline=True)
        await  ctx.send(embed=embed)

    @help.command(name="disconnect")
    async def disconnect(self, ctx):
        embed = Embed(description="**`Arif leaves voice channel**", colour=ctx.author.colour,
                      timestamp=datetime.datetime.utcnow())
        embed.set_author(name="Disconnect")
        embed.add_field(name="Exp", value="**`Arif.disconnect`**", inline=True)
        embed.add_field(name="Aliases", value="**`Arif.leave`**", inline=True)
        await  ctx.send(embed=embed)

    @help.command(name="userinfo")
    async def user_Info(self, ctx):
        embed = Embed(description="Userinfo", colour=ctx.author.colour,
                      timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Usage", value="**`Arif.userinfo`**", inline=True)
        embed.add_field(name="Return",
                        value="**`If you dont give a user return info about you.(Arif.userinfo @Arog'tan Arif) return specified user  account information.`**",
                        inline=True)
        await  ctx.send(embed=embed)

    @help.command(name="SvInfo")
    async def sv_Info(self, ctx):
        embed = Embed(description="**`Server information`**", colour=ctx.author.colour,
                      timestamp=datetime.datetime.utcnow())
        embed.set_author(name="SvInfo")
        embed.add_field(name="**`Usage`**", value="**`Arif.SvInfo or Arif.vInfo`**", inline=True)
        await  ctx.send(embed=embed)

    @help.command(name="setupLogChannel")
    async def setupLogChannel(self, ctx):
        embed = Embed(description="**`SetupLogChannel usage`**", colour=ctx.author.colour,
                      timestamp=datetime.datetime.utcnow())
        embed.set_author(name="**`Setup Log Channel`**")
        embed.add_field(name="Usage", value="**`Arif.SvInfo or Arif.vInfo`**", inline=True)
        embed.add_field(name="Info",
                        value="**`Arif creates named log channel and userprofle,username,message edit,message delete all this triggered sends log channel.(Everyone can see and write this channel)`**",
                        inline=True)
        await  ctx.send(embed=embed)

    @help.command(name="RockPaperScissors")
    async def RockPaperScissor(self, ctx):
        embed = Embed(description="**`Rock-Paper-Scissors Game`**", colour=ctx.author.colour,
                      timestamp=datetime.datetime.utcnow())
        embed.set_author(name="Game")
        embed.add_field(name="Usage",
                        value="**`Arif.RockPaperScissors 'and your choice' after bot return his choice and who is winner.`**",
                        inline=True)
        await  ctx.send(embed=embed)

    @help.command(name="lyrics")
    async def lyrics(self, ctx):
        embed = Embed(
            description="**`Returns current music lyrics if not text length is high.İf  text length is high returns to you lyrics link.`**",
            colour=ctx.author.colour,
            timestamp=datetime.datetime.utcnow())
        embed.add_field(name="**`Usage`**", value="**`Arif.lyrics`**", inline=True)
        embed.set_author(name="Lyrics")
        await  ctx.send(embed=embed)

    @help.command(name="loop")
    async def loop(self, ctx):
        embed = Embed(
            description="**`Start loop a current music,when used this command second time loop is turned off.`**",
            colour=ctx.author.colour,
            timestamp=datetime.datetime.utcnow())
        embed.add_field(name="**`Usage`**", value="**`Arif.loop`**", inline=True)
        embed.set_author(name="Loop")
        await  ctx.send(embed=embed)

    @help.command(name="shuffle")
    async def shuffle(self, ctx):
        embed = Embed(
            description="**`Shuffles the queue if queue not empty.`**",
            colour=ctx.author.colour,
            timestamp=datetime.datetime.utcnow())
        embed.set_author(name="Shuffle")
        embed.add_field(name="**`Usage`**", value="**`Arif.shuffle`**", inline=True)

        await  ctx.send(embed=embed)

    @help.command(name="queue")
    async def queue(self, ctx):
        embed = Embed(
            description="**`List of queued songs`**",
            colour=ctx.author.colour,
            timestamp=datetime.datetime.utcnow())
        embed.set_author(name="Queue")
        embed.add_field(name="**`Usage`**", value="**`Arif.queue`**", inline=True)
        embed.add_field(name="**`Aliases`**", value="**`Arif.playlist`**", inline=True)

        await  ctx.send(embed=embed)

    @help.command(name="removefromqueue")
    async def removefromqueue(self, ctx):
        embed = Embed(
            description="**`Removes the numbered song from the queue.`**",
            colour=ctx.author.colour,
            timestamp=datetime.datetime.utcnow())
        embed.set_author(name="Remove from Queue")
        embed.add_field(name="**`Usage`**", value="Arif.removequeue <number 1-:infinity:>", inline=True)

        await  ctx.send(embed=embed)

    @help.command(name="skip")
    async def skip(self, ctx):
        embed = Embed(
            description="**`If there is a next song.Arif skips current song.`**",
            colour=ctx.author.colour,
            timestamp=datetime.datetime.utcnow())
        embed.set_author(name="Skip")
        embed.add_field(name="**`Usage`**", value="**`Arif.skip´**", inline=True)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Information(bot))
