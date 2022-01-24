import asyncio
import datetime

import discord
from discord import Embed
from discord.ext import commands
import random

choices = ["Rock", "Paper", "Scissors"]


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="RockPaperScissors")
    async def Rock_Paper_Scissors(self, ctx, choice: str):
        bot_choice = random.choice(choices)
        await  ctx.send(f"My choice {bot_choice} ")
        user_choice = choice.capitalize()
        if not user_choice.isdigit():
            if user_choice in choices:
                if user_choice == bot_choice:
                    await  ctx.send("Draw! GG")
                elif user_choice == "Rock":
                    if bot_choice == "Paper":
                        await ctx.send("You lost :)! GG")
                    else:
                        await ctx.send("You win -_- ! GG")
                elif user_choice == "Paper":
                    if bot_choice == "Rock":
                        await ctx.send("You win -_-! GG")
                    else:
                        await ctx.send("You lost :)! GG")
                elif user_choice == "Scissors":
                    if bot_choice == "Rock":
                        await ctx.send("You lost :)! GG")
                    else:
                        await ctx.send("You win -_-! GG")
            else:
                await ctx.send("You must chose Rock-Paper-Scissors.")
        else:
            await ctx.send("You must chose Rock-Paper-Scissors.")

    @commands.command(name="CoinFlip", aliases=["coinflip"])
    async def CoinFlip(self, ctx):
        if random.randint(0, 1) == 0:
            embed = Embed(title="CoinFlip", description=f"{ctx.author.mention} Flipped coin, we got **Heads**!")
            await ctx.send(embed=embed)
        else:
            embed = Embed(title="CoinFlip", description=f"{ctx.author.mention} Flipped coin, we got **Tails**!")
            await ctx.send(embed=embed)

    @commands.command(name="Bigtext", aliases=["bigtext"])
    async def big_text(self, ctx, *, text: str):
        input = text.lower()
        regional_indicator_list = []
        for item in input:
            regional_indicator_list.append(f":regional_indicator_{item}:")
        await ctx.send("".join(regional_indicator_list))

    @big_text.error
    async def big_text_error(self, ctx, exc):
        if isinstance(exc, Exception):
            embed = Embed(title=" :x: Missing Argument",
                          description="The text argument is required. \n Usage: Arif.bigtext <text>",
                          colour=ctx.author.colour, timestamp=datetime.datetime.utcnow())
            await ctx.message.add_reaction("❌")
            await ctx.send(embed=embed)

    @commands.command(name="NumberGuess", aliases=["numberguess"])
    async def number_guess(self, ctx):
        number = random.randint(0, 101)
        attempt_count = 5
        await ctx.send("Welcome to number guess! \nNumber is between 0-100,You have 5 guessing.Good Luck")
        await asyncio.sleep(1)
        await ctx.send(f"{ctx.author.mention} Make your guess.")

        def check(m: discord.Message):
            return m.author == ctx.author

        guess = await discord.ext.commands.Bot.wait_for(event='message', check=check, timeout=60.0)

        while guess.content != number and attempt_count >= 1:
            if guess.content > number:
                await ctx.send("Your guess is higher than number.")
                attempt_count -= 1
            elif guess.content < number:
                await ctx.send("Your guess is lowe than number.")
                attempt_count -= 1
            await ctx.send(f"{ctx.author.mention} Make your guess.")
            guess = ctx.wait_for('message', check=check)
        else:
            await ctx.send(f"YOU WIN Number:{number}")

    @number_guess.error
    async def number_guess_error(self, ctx, exc):
        if isinstance(exc, TypeError):
            embed = Embed(title=" :x: Type Error",
                          description="The you must enter numeric values",
                          colour=ctx.author.colour, timestamp=datetime.datetime.utcnow())
            await ctx.message.add_reaction("❌")
            await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Game(client))
