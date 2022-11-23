import discord
from discord.ext import commands
from discord import app_commands, channel
import utilities
from discord.ext import tasks
from datetime import datetime, timedelta
current_date = datetime.utcnow()
new_time = current_date.strftime('%d-%m-%Y')
tommorow = current_date + timedelta(days=1)
new_tommorow_time = tommorow.strftime('%d-%m-%Y')



class huiswerk(commands.Cog):
    """Huiswerk notificaties."""
    def __init__(self, bot:commands.Bot) -> None:
        global hw_channel
        global reminder_channel
        self.bot = bot
        hw_channel = self.bot.get_channel(981263225817550922)
        reminder_channel = self.bot.get_channel(1038431010804731907)



    @app_commands.command(name="huiswerkcheck", description="Kijk of er opdrachten zijn vandaag.")
    # Check of er huiswerk is dat VANDAAG af moet zijn.
    async def huiswerk_check(self, interaction : discord.Interaction):
        sendMessage = ""
        db = await utilities.connect_database()
        await utilities.check_huiswerk_vandaag()
        async with db.execute(f"SELECT vak, opdracht, url FROM huiswerk WHERE time = ? ", (str(new_time),))as results:
            await interaction.response.send_message("Huiswerk laden...")
            async for entry in results:
                vak, opdracht, url = entry
                sendMessage += f"Vak: {vak}\nOpdracht: {opdracht}\nTe vinden op: {url}\n=========\n\n"

                if entry is None:
                    return await interaction.response.send_message("Geen huiswerk voor vandaag.")
        try:
            await db.close()
        except ValueError:
            pass
        try:
            await interaction.edit_original_response(content = sendMessage) 
        except discord.errors.HTTPException:
            return await interaction.edit_original_response(content="**Geen huiswerk voor vandaag.**")
    @app_commands.command(name="huiswerkadd", description="Voeg huiswerk toe. ")
    # Voeg huiswerk toe
    async def additem(self, interaction : discord.Interaction, vak:str, opdr:str, url:str, deadline:str):
        db = await utilities.connect_database()
        await db.execute(F"INSERT OR IGNORE INTO huiswerk VALUES (?, ?, ?, ?)", (vak, opdr, url, deadline, ))
        await db.commit()
        try:
            await db.close()
        except ValueError:
            pass
        return await interaction.response.send_message(f"{vak} -- {opdr}  op {url} met de deadline {deadline} is toegevoegd aan de database.")


    @app_commands.command(name="deletehw", description="Verwijder huiswerk uit de database.")
    # Verwijder huiswerk van de database.
    async def deletehw(self, interaction : discord.Interaction, url: str):
        db = await utilities.connect_database()
        await db.execute("DELETE FROM HUISWERK WHERE url = ?", (url, ))
        await db.commit()
        return await interaction.response.send_message(f"Verwijdered {url} van de huiswerk database.")


    @tasks.loop(seconds=10)
    async def school():
        database = await utilities.connect_database()
        await database.execute("CREATE TABLE IF NOT EXISTS schooltime (datum TEXT, tijd, TEXT)")
        await database.commit()
        async with database.execute("SELECT tijd FROM schooltime WHERE datum = ?", (new_tommorow_time,)) as schooltijd:
            async for entry in schooltijd:
                tijd = entry
            await reminder_channel.send(f'**NIET VERGETEN** Je moet morgen om {tijd[0]} op school zijn!')
    
    #school.start()
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(huiswerk(bot))

