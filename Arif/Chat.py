import asyncio

import discord
import openai
from chronological import cleaned_completion
from discord.ext import commands


class Chat(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="chat",with_app_command=True, help="Ask any question to Arif",pass_context=True)
    async def Chat(self, ctx, *, question: str):
        async  with ctx.typing():
            response = openai.Completion.create(model="text-davinci-003", prompt=question, temperature=0,
                                            max_tokens=1000)
            await  asyncio.sleep(120)

        await  ctx.send(response.choices[0].text,ephemeral= True)


async def setup(bot):
    await bot.add_cog(Chat(bot))
