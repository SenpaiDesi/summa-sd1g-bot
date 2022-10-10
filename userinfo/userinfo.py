import discord
from discord import app_commands, user
from typing import Literal, Optional
from discord.app_commands import Choice
from discord.ext import commands
class userinfo(commands.Cog):
    """Gebruikers informatie."""
    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
    
    @app_commands.command(name="whois", description="Krijg informatie over een user.", auto_locale_strings=True)
    @app_commands.describe(user="Selecteer de gebruiker. Geen gebruiker = jezelf")
    async def whois(self, interaction:discord.Interaction, user: Optional[discord.Member] = None):
        if user is None:
            user = interaction.user
        date_format = "%a, %d %b %Y %I:%M %p"
        embed = discord.Embed(color=discord.Color.orange(), description=user.mention)
        embed.set_author(name=str(user), icon_url=user.avatar.url)
        embed.set_thumbnail(url=user.avatar.url)
        embed.add_field(name="Joined", value=user.joined_at.strftime(date_format), inline=False)
        members = sorted(interaction.guild.members, key=lambda m: m.joined_at)
        embed.add_field(name="Join position", value=str(members.index(user) + 1), inline=False)
        embed.add_field(name="Registered", value=user.created_at.strftime(date_format), inline=False)

        if len(user.roles) > 1:
            role_string = ' '.join([r.mention for r in user.roles][1:])
            embed.add_field(name="Roles [{}]".format(len(user.roles) - 1), value=role_string, inline=False)
            embed.set_footer(text='ID: ' + str(user.id))
            return await interaction.response.send_message(embed=embed)
        else:
            embed.add_field(name="Roles:", value="None")
            return await interaction.response.send_message(embed=embed)

    @app_commands.command(name='av', description="Krijg de avatar (Profiel foto) van een gebruiker")
    @app_commands.describe(member= "Kies een gebruiker.")
    async def av(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        if member is None:
            member = interaction.user
        else:
            await interaction.response.send_message(member.avatar.url)







async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(userinfo(bot))