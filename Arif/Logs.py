import asyncio
import datetime

from discord.ext import commands


class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @commands.Cog.listener()
    async def on_member_update(self, ctx, before, after):
        if before.display_name != after.display_name:
            while not self.bot.is_closed():
                with open("stats.txt", "a") as file:
                    file.write(
                        f"Time:{datetime.datetime.utcnow()},Description:Nickname Change,Server:{ctx.guild.name},Before:{before.display_name},After:{after.display_name}")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not after.author.bot:
            pass

    @commands.Cog.listener()
    async def on_message_delete(self, before, after):
        if not after.author.bot:
            pass


def setup(client):
    client.add_cog(Logs(client))
