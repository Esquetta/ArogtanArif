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
        user_choice=choice.capitalize()
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


def setup(client):
    client.add_cog(Game(client))
