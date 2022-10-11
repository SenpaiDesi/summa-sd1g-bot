import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
from links import linkaddr

class faq(commands.Cog):
    """faq links"""
    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="links", description="Vind hier de meest gevraagde links.")
    @app_commands.describe(link_type = "Kies de link die je wil vinden.")
    @app_commands.choices(link_type = [
        Choice(name="Itslearning", value="itslearning"),
        Choice(name="Rooster", value="rooster"),
        Choice(name="Wachtwoord Reset/Veranderen", value="paswdreset")
        #Choice(name="unban ticket", value="unban"),
        #Choice(name="Anticheat Unban ticket", value="acunban")
    ])
    async def subticket(self, interaction:discord.Interaction, link_type:str):
        channel = self.bot.get_channel(1024327971374387241)
        if link_type == "itslearning":
            await interaction.response.send_message(f"Je kunt itslearning vinden op <{linkaddr.itslearning}>")
        elif link_type == "rooster":
            await interaction.response.send_message(f"Je kunt je rooster vinden op: <{linkaddr.rooster}>", ephemeral=False)
        elif link_type == "paswdreset":
            await interaction.response.send_message(f"Je kunt je wachtwoord resetten / veranderen op: <{linkaddr.password_reset}>", ephemeral=False)
        #elif link_type == "unban":
            #await interaction.response.send_message(f"Ticket created at {channel.mention}", ephemeral=False)
        #elif link_type == "acunban":
            #await interaction.response.send_message(f"Ticket created at {channel.mention}", ephemeral=False)






async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(faq(bot))