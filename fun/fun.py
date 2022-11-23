import discord
from discord import AudioSource, VoiceChannel, app_commands, channel, voice_client, FFmpegAudio, FFmpegOpusAudio
from discord.ext import commands
from discord.app_commands import Choice
import ffmpeg
import requests
import json
from jokeapi import Jokes
from dadjokes import Dadjoke

class fun(commands.Cog):
    """fun commands."""
    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
        dadjoke = Dadjoke()

    @app_commands.command(name="meme", description="Get a funny meme")
    async def meme(self, interaction : discord.Interaction):
        response = requests.get('https://meme-api.herokuapp.com/gimme')
        data = response.json()
        await interaction.response.send_message(data["url"])

    @app_commands.command(name="joke", description="Wie wil er nou niet grappig zijn?")
    @app_commands.describe(joke="Type joke")
    @app_commands.choices(joke = [
        Choice(name="Dad joke", value="dadjoke"),
        Choice(name="Dark humor", value="darkhumor"),
        Choice(name="Programming", value="programming"),
        Choice(name="Spooky", value="spooky")
    ])
    async def joke(self, interaction : discord.Interaction, joke:str):
        j = await Jokes()
        if joke == "dadjoke":
            dadjoke = Dadjoke()
            await interaction.response.send_message(dadjoke.joke)
        elif joke == "darkhumor":
            joke = await j.get_joke(category=['Dark'])
            try:
                written = joke['joke']
                await interaction.response.send_message(written)
            except KeyError:
                setup = joke["setup"]
                delivery = joke["delivery"]
                await interaction.response.send_message(f"{setup}\n{delivery}")
        elif joke == "programming":
            joke = await j.get_joke(category=["Programming"])
            try:
                written = joke['joke']
                await interaction.response.send_message(written)
            except KeyError:
                setup = joke["setup"]
                delivery = joke["delivery"]
                await interaction.response.send_message(f"{setup}\n{delivery}")
        elif joke == "spooky":
            joke = await j.get_joke(category=["Spooky"])
            try:
                written = joke['joke']
                await interaction.response.send_message(written)
            except KeyError:
                setup = joke["setup"]
                delivery = joke["delivery"]
                await interaction.response.send_message(f"{setup}\n{delivery}")
        else:
            return await interaction.response.send_message("Sorry dit type joke is nog niet geimplementeerd.")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(fun(bot))
