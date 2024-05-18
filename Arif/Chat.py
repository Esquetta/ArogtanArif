import asyncio

import discord
import openai
from chronological import cleaned_completion
from discord.ext import commands


class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="chat", with_app_command=True,
                             help="Ask any question to Arif,it could may take a few minitues to answer.",
                             pass_context=True)
    async def Chat(self, ctx, *, question: str):
        try:
            async with ctx.typing():
                response = openai.chat.completions.create(model='gpt-4o',
                                                     messages=[{'role': 'user', 'content': question}],
                                                     max_tokens=150)
                await  asyncio.sleep(1)
                await  ctx.send(response.choices[0].message.content, ephemeral=True)

        except Exception as e:
            await ctx.send(f"An error accured {e}")


async def setup(bot):
    await bot.add_cog(Chat(bot))
