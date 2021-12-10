from discord.ext import commands



class Logs(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass
    @commands.Cog.listener()
    async def on_member_update(self,before,after):
        pass
    @commands.Cog.listener()
    async  def  on_message_edit(self,before,after):
        if not after.author.bot:
            pass
    @commands.Cog.listener()
    async  def on_message_delete(self,before,after):
        if not after.author.bot:
            pass












def setup(client):
    client.add_cog(Logs(client))