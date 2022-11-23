import discord
from discord.ext import commands
from discord import app_commands
import random
async def randomizer():
    global randomizer_calc_result
    randomizer_calc = await random.randint(0,100)
    if randomizer_calc > 80:
        randomizer_calc_result = "ad"
    else:
        randomizer_calc_result = "noad"
    return randomizer_calc_result

    

class events(commands.Cog):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_interaction(interaction):
        await randomizer()
        if randomizer_calc_result == "ad":
            await interaction.channel.send("Wil je je eigen discord bot? Ga dan naar <https://codechaos.net>")
        else:
            return
            





async def setup(bot : commands.Bot) -> None:
   await bot.add_cog(events(bot))