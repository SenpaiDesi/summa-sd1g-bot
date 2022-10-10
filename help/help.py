import discord
import utilities
from discord.errors import Forbidden
from discord.ext import commands


async def send_embed(ctx, embed):
    """
    Function that handles the sending of embeds
    """
    try:
        await ctx.send(embed=embed)
    except Forbidden:
        try:
            await ctx.send("Hey, seems like I can't send embeds. Please check my permissions :)")
        except Forbidden:
            await ctx.author.send(f"Hey, seems like I can't send any message in {ctx.channel.name} in {ctx.guild.name}\n"f"Please inform an admin / Owner.", embed=embed)


class help(commands.Cog):
    """De command die je nu gebruikt."""
    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def help(self, ctx, *input):
        """Shows a beutifull help command. """
        version = "0.1 ALPHA"

        if not input:
            emb = discord.Embed(title="Commands and modules", color=discord.Color.random(), description=f"Use {ctx.prefix}help <module> to gain more information about that module.")
            cogs_desc = ''
            for cog in self.bot.cogs:
                cogs_desc += f'`{cog}` {self.bot.cogs[cog].__doc__}\n'

            emb.add_field(name="Modules", value=cogs_desc, inline=False)

            commands_desc = ''
            for command in self.bot.walk_commands():
                if not command.cog_name and not command.hidden:
                    commands_desc += f"`{command.name}` - {command.help}\n"

            if commands_desc:
                emb.add_field(name='Not belonging to a module', value=commands_desc, inline=False)

            emb.add_field(name="About", value=f"This bot is currenly being developed by Senpai_Desi#4108.")
            emb.set_footer(text=f"Running {version}.")

        elif len(input) == 1:
            for cog in self.bot.cogs:
                if cog.lower() == input[0].lower():
                    emb = discord.Embed(title=f"{cog} - Commands", description=self.bot.cogs[cog].__doc__, color=discord.Color.random())

                    for command in self.bot.get_cog(cog).get_commands():
                        if not command.hidden:
                            emb.add_field(name=f"`{ctx.prefix}{command.name}`", value=command.help, inline=False)
                    break
                else:
                    emb = discord.Embed(title="Oh no!", description=f"Ik ken deze module niet. {input[0]}.", color=discord.Color.red())

        elif len(input) > 1:
            emb = discord.Embed(title="Hoho, rustig aan", description=f"Gebruik maar een module per keer alsjeblieft.", color=discord.Color.gold())

        else:
            emb = discord.Embed(title="Sorry ik kan op dit moment de commands niet laden.", color=discord.Color.red())

        await send_embed(ctx, emb)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(help(bot))