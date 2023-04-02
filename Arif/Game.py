import asyncio
import datetime

import discord
from discord import Embed
from discord.ext import commands
from discord import Interaction
from discord.ui import View, Button
import random

choices = ["Rock", "Paper", "Scissors"]


class RockPaperScissorsButtons(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
        self.bot_Choice = random.choice(choices)

    @discord.ui.button(style=discord.ButtonStyle.grey, label="🪨", custom_id="btn_Rock")
    async def RockButton(self, interaction: Interaction, button: Button):
        if "Rock" == self.bot_Choice:
            await  interaction.response.send_message("Draw! GG", ephemeral=True)
        else:
            if self.bot_Choice == "Paper":
                await interaction.response.send_message("I picked 📄, You lost :) GG!", ephemeral=True)
            else:
                await  interaction.response.send_message("I picked ✂️,You win GG!", ephemeral=True)

        button.disabled = True

    @discord.ui.button(style=discord.ButtonStyle.grey, label="📄", custom_id="btn_Paper")
    async def PaperButton(self, interaction: Interaction, button: Button):
        if "Paper" == self.bot_Choice:
            await  interaction.response.send_message("Draw! GG", ephemeral=True)
        else:
            if self.bot_Choice == "Scissors":
                await interaction.response.send_message("I picked ✂️, You lost :) GG!", ephemeral=True)
            else:
                await  interaction.response.send_message("I picked 📄,You win GG!", ephemeral=True)
        button.disabled = True

    @discord.ui.button(style=discord.ButtonStyle.grey, label="✂️", custom_id="btn_Scissors")
    async def ScissorsButton(self, interaction: Interaction, button: Button):
        if "Scissors" == self.bot_Choice:
            await  interaction.response.send_message("Draw! GG", ephemeral=True)
        else:
            if self.bot_Choice == "Rock":
                await interaction.response.send_message("I picked 🪨, You lost :) GG!", ephemeral=True)
            else:
                await  interaction.response.send_message("I picked 📄,You win GG!", ephemeral=True)
        button.disabled = True


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="rockpaperscissors", with_app_command=True, help="Starts Rock-Paper-Scissors game.")
    async def Rock_Paper_Scissors(self, ctx):
        await  ctx.send("Pick one", view=RockPaperScissorsButtons(), ephemeral=True)

    @commands.hybrid_command(name="coinflip", with_app_command=True, help="Flip's a coin.")
    async def CoinFlip(self, ctx):
        if random.randint(0, 1) == 0:
            embed = Embed(title="CoinFlip", description=f"{ctx.author.mention} Flipped coin, we got **Heads**!")
            await ctx.send(embed=embed)
        else:
            embed = Embed(title="CoinFlip", description=f"{ctx.author.mention} Flipped coin, we got **Tails**!")
            await ctx.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(name="bigtext", with_app_command=True, help="Returns your input to big text.")
    async def big_text(self, ctx, *, text: str):
        input = text.lower()
        regional_indicator_list = []
        for item in input:
            regional_indicator_list.append(f":regional_indicator_{item}:")
        await ctx.send("".join(regional_indicator_list), ephemeral=True)

    @big_text.error
    async def big_text_error(self, ctx, exc):
        if isinstance(exc, Exception):
            embed = Embed(title=" :x: Missing Argument",
                          description="The text argument is required. \n Usage: Arif.bigtext <text>",
                          colour=ctx.author.colour, timestamp=datetime.datetime.utcnow())
            await ctx.message.add_reaction("❌")
            await ctx.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(name="numberguess", with_app_command=True, help="Start's a number guessing game.")
    async def number_guess(self, ctx):
        number = random.randint(0, 101)
        attempt_count = 5
        await ctx.send("Welcome to number guess! \nNumber is between 0-100,You have 5 guessing.Good Luck")
        await asyncio.sleep(1)
        await ctx.send(f"{ctx.author.mention} Make your guess.")

        def check(m: discord.Message):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        try:
            msg = await self.bot.wait_for(event='message', check=check, timeout=60.0)
            guess = int(msg.content)
        except asyncio.TimeoutError:
            await ctx.send(
                f"**{ctx.author}**, you didn't send any guess that meets the check in this channel for 60 seconds..")
            return
        else:
            while guess != number:
                if guess > number and attempt_count >= 1:
                    await ctx.send("Your guess is higher than number.")
                    await ctx.send(f"Guessing:{attempt_count}")
                    attempt_count -= 1
                elif guess < number and attempt_count >= 1:
                    await ctx.send("Your guess is lower than number.")
                    await ctx.send(f"Guessing:{attempt_count}")
                    attempt_count -= 1
                else:
                    await ctx.send("You're out of guessing.")
                    await ctx.send(f"Number:{number}")
                    break
                await ctx.send(f"{ctx.author.mention} Make your guess.")
                try:
                    msg = await self.bot.wait_for(event='message', check=check, timeout=60.0)
                    guess = int(msg.content)
                except asyncio.TimeoutError:
                    await ctx.send(
                        f"**{ctx.author}**, you didn't send anyg guess that meets the check in this channel for 60 seconds..")
                    return
            else:
                await ctx.send(f"**YOU WIN {ctx.author} \nNumber:{number}**")

    @number_guess.error
    async def number_guess_error(self, ctx, exc):
        if isinstance(exc, Exception):
            await ctx.message.add_reaction("❌")
            await ctx.send("You must enter numeric value.", ephemeral=True)

    @commands.hybrid_command(name="rolldice", with_app_command=True, help="Rolls a dice and returns dice number.")
    async def Roll_Dice(self, ctx):
        dice = ["one", "two", "three", "four", "five", "six"]
        await ctx.send(f":{random.choice(dice)}:", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Game(bot))
