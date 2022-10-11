import discord
from discord.ext import commands
from discord import app_commands, channel
import utilities
from discord.ext import tasks
from datetime import datetime
current_date = datetime.utcnow()
new_time = current_date.strftime('%d-%m-%Y')



class huiswerk(commands.Cog):
    """Huiswerk notificaties."""
    def __init__(self, bot:commands.Bot) -> None:
        global hw_channel
        self.bot = bot
        hw_channel = self.bot.get_channel(981263225817550922)


    @commands.command(name="huiswerkcheck", description="Kijk of er opdrachten zijn vandaag.")
    async def huiswerk_check(self, ctx):
        db = await utilities.connect_database()
        await utilities.check_huiswerk_vandaag()
        async with db.execute(f"SELECT vak, opdracht, url FROM huiswerk WHERE time = ? ", (str(new_time),))as results:
            await ctx.send("Huiswerk voor vandaag:")
            async for entry in results:
                vak, opdracht, url = entry
                if entry is None:
                    return await ctx.send("Geen huiswerk voor vandaag.")
                else:
                    await ctx.send(f"Vak: {vak}\nOpdracht: {opdracht}\nTe vinden op: {url}\n=========\n\n") 
        try:
            await db.close()
        except ValueError:
            pass
    
    @commands.command(name="huiswerkadd")
    async def additem(self, ctx, vak:str, opdr:str, url:str, deadline:str):
        db = await utilities.connect_database()
        await db.execute(F"INSERT OR IGNORE INTO huiswerk VALUES (?, ?, ?, ?)", (vak, opdr, url, deadline, ))
        await db.commit()
        try:
            await db.close()
        except ValueError:
            pass
        return await ctx.send(f"{vak} -- {opdr}  op {url} met de deadline {deadline} is toegevoegd aan de database.")


    @app_commands.command(name="deletehw", description="Verwijder huiswerk uit de database.")
    async def deletehw(self, interaction : discord.Interaction, url: str):
        db = await utilities.connect_database()
        await db.execute("DELETE FROM HUISWERK WHERE url = ?", (url, ))
        await db.commit()
        return await interaction.response.send_message(f"Verwijdered {url} van de huiswerk database.")





async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(huiswerk(bot))

