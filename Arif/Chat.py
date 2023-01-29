import discord
import openai
from chronological import cleaned_completion
from discord.ext import commands


class Chat(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="Chat", help="Ask any question to Arif", aliases=["Chat,Ask"], pass_context=True)
    async def Chat(self, ctx,*, question: str):
        response = openai.Completion.create(model="text-davinci-003", prompt=question, temperature=0, max_tokens=1000)
        await  ctx.send(response.choices[0].text)


async def setup(bot):
    await bot.add_cog(Chat(bot))
