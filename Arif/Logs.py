import datetime
import discord
from discord import Embed
from discord.ext import commands

from Db.Entities.Servers import Servers
from Db.db import Set_Server, Get_Server, Set_LogChannel, Get_SvInfo, Get_LogChannel, Delete_LogChannel, Delete_Sv
from Db.Entities.LogChannels import LogChannels
from discord.utils import find


class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        '''channel=Get_Server(id=self.bot.guild.id)
        if len(channel>0):
            self.log_channel_id=channel[0][3]
            print(f"Log Channel Found {self.bot.guild.name}")'''
        self.log_channel_id = None
        self.log_channel = self.bot.get_channel(self.log_channel_id)

    @commands.command(name="setupLogChannel", help="Creates log chanel with everyone can see and writes text messages",
                      aliales=["setlogChannel", "LogChannelSetup"])
    async def setup_log_channel(self, ctx):
        channel = Get_Server(id=ctx.guild.id)
        if len(channel) > 0:
            await ctx.send("Already created log channnel")
        else:
            overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(read_messages=True),
                          ctx.guild.me: discord.PermissionOverwrite(read_messages=True)}
            log_channel = await  ctx.guild.create_text_channel('Logs', overwrites=overwrites)
            Server = Servers()

            Server.ServerId = ctx.guild.id
            Server.ServerName = ctx.guild.name
            Set_Server(Server=Server)
            server = Get_SvInfo(svId=ctx.guild.id)
            LogChannel = LogChannels()
            LogChannel.ChanelId = log_channel.id
            LogChannel.ServerDbId = server[0][0]
            Set_LogChannel(LogChannel)
            self.log_channel_id = log_channel.id
            self.log_channel = log_channel
            await  ctx.send("Setup completed.")

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if before.avatar_url != after.avatar_url:
            embed = Embed(title="Member update", description="Avatar Change  This is old one =>", colour=after.colour,
                          timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=before.avatar_url)
            embed.set_image(url=after.avatar_url)

            await self.log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.display_name != after.display_name:
            embed = Embed(title="Member update", description="Nickname Change", colour=after.colour,
                          timestamp=datetime.datetime.utcnow())
            fields = [("Before:", f"{before.display_name}", True), ("After:", f"{after.display_name}", True)]
            try:
                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)
                await self.log_channel.send(embed=embed)
            except AttributeError as attributeError:
                await  self.bot.guild.text_channels[0].send(
                    "You need to specified text channel.exp:Arif.setLogChannel 'your channel id here' (right click text channel copy id) ")
        elif before.roles != after.roles:
            embed = Embed(title="Member update", description="Role updates", colour=after.colour,
                          timestamp=datetime.datetime.utcnow())
            fields = [("Before:", ",".join([i.mention for i in before.roles[1:]]), True),
                      ("After:", ",".join([i.mention for i in after.roles[1:]]), True)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            await self.log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not after.author.bot:
            if before.content != after.content:
                embed = Embed(title="Message update", description="Message updates", colour=after.author.colour,
                              timestamp=datetime.datetime.utcnow())
                fields = [("Edited By:", f"@{before.author}", True),
                          ("Before:", before.content, True),
                          ("After:", after.content, True)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)
                await self.log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.author.bot:
            embed = Embed(title="Message update", description="Message updates", colour=message.author.colour,
                          timestamp=datetime.datetime.utcnow())
            fields = [("Deleted By:", f"@{message.author}", True),
                      ("Content:", message.content, True)
                      ]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            await self.log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        channel_Db = Get_LogChannel(channel.id)
        if len(channel_Db) > 0:
            Delete_LogChannel(channel.id)
            Delete_Sv(channel_Db[0][2])
        else:
            print("This channel is not log channel.")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        try:
            cli = self.bot
            ctx = cli.get_context
            general = find(lambda x: x.name == 'general' or 'genel', guild.text_channels)
            if general:
                if general and general.permissions_for(guild.me).send_messages:
                    await guild.text_channels[0].send(
                        f"Hello {guild.name}! I am {self.bot.user.display_name}. Thank you for inviting me.\n\nTo see "
                        f"what commands I have available type `Arif.help`.\n")
                    Server = Get_Server(id=guild.id)
                    if len(Server) > 0:
                        print("Server and log channel detected")
                        self.log_channel_id = Server[0][3]
        except PermissionError:
            pass

    @commands.command(name="Say", aliases=["say"])
    async def say(self, ctx,*,say: str):
        await ctx.send(f"{say}")


def setup(client):
    client.add_cog(Logs(client))
