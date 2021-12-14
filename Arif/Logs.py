import datetime
import discord
from discord import Embed
from discord.ext import commands
from discord.ext.commands import UserInputError


class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.log_channel_id = 0
        self.log_channel = self.bot.get_channel(self.log_channel_id)

    @commands.command(name="setupLogChannel", help="Creates log chanel with everyone can see and writes text messages",
                      aliales=["setlogChannel", "LogChannelSetup"])
    async def setup_log_channel(self, ctx):
        for channel in ctx.guild.text_channels:
            if channel.name == "log":
                await  ctx.send("Channel exist.")
        overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(read_messages=True),
                      ctx.guild.me: discord.PermissionOverwrite(read_messages=True)}
        log_channel = await  ctx.guild.create_text_channel('Logs', overwrites=overwrites)
        self.log_channel_id = log_channel.id
        self.log_channel = self.bot.get_channel(self.log_channel_id)
        await  ctx.send("Setup completed.")

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if before.avatar_url != after.avatar_url:
            embed = Embed(title="Member update", description="Avatar Change  This is old one =>", colour=after.colour,
                          timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=before.avatar_url)
            embed.set_image(url=after.avatar_url)
            try:
                await self.log_channel.send(embed=embed)
            except AttributeError as attributeError:
                await  self.bot.guild.text_channels[0].send(
                    "You need to specified text channel.exp:Arif.setLogChannel 'your channel id here' (right click text channel copy id) ")

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
                fields = [("Edited By:",f"@{before.author}", True),
                        ("Before:", before.content, True),
                          ("After:", after.content, True)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)
                await self.log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self,message):
        if not message.author.bot:
            embed = Embed(title="Message update", description="Message updates", colour=message.author.colour,
                          timestamp=datetime.datetime.utcnow())
            fields = [("Deleted By:", f"@{message.author}", True),
                      ("Content:", message.content, True)
                      ]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            await self.log_channel.send(embed=embed)


def setup(client):
    client.add_cog(Logs(client))