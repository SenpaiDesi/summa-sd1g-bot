import discord
from discord.ext import commands
import utilities


class admins(commands.Cog):
    """Admin commands alleen te gebruiken door de bot creator"""
    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="dbsetup")
    @commands.is_owner()
    async def dbsetup(self, ctx):
        infomsg = await ctx.send("Setting up db.")
        db = await utilities.connect_database()
        await db.execute("CREATE TABLE IF NOT EXISTS huiswerk (vak TEXT, opdracht TEXT, url TEXT, time TEXT)")
        await db.commit()
        await db .execute("CREATE TABLE IF NOT EXISTS moderationLogs (logid INTEGER PRIMARY KEY, guildid INTEGER, moderationLogType INTEGER, userid INTEGER, moduserid INTEGER, content VARCHAR, duration INTEGER)")
        await db.commit()
        await infomsg.edit(content="Done")
        try:
            await db.close()
        except ValueError:
            pass
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(admins(bot))