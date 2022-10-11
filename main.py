from discord import activity, app_commands
import utilities
import discord
from discord.ext import commands
from discord.ext.commands import Greedy, Context
from typing import Literal, Optional
import assets
MY_GUILD = discord.Object(id=981263222545989722)   # mijn server 981263222545989722  summa server 1016352713010855976

intents = discord.Intents.all()
intents.message_content = True
 
 # Zet de basis prefix naar sd-
class MyBot(commands.Bot):
    def __init__(self, intents= intents):
        super().__init__(intents=intents, command_prefix="sd-", application_id = 1027135965891923988)
    # Sync de slash commands (/)
    async def setup_hook(self):
        await bot.tree.sync()

    # Laad de extensies (aka andere files.)
    async def on_ready(self):
        link = utilities.load_json(assets.jsonfile)
        linkurl = link["url"]
        print(f"[INFO]  {self.user} has connected to the discord gateaway!\n")
        for extension in assets.modules:
            await bot.load_extension(extension)
            print(f"[INFO]  Loaded {extension}")
        print(f"[INFO]  {linkurl}\n")
            

bot = MyBot()
bot.remove_command("help")

# Uitleg voor command syncing. Alleen te gebruiken voor development.
"""sd-sync -> global sync
sd-sync ~ -> sync current guild
sd-sync * -> copies all global app commands to current guild and syncs
sd-sync ^ -> clears all commands from the current guild target and syncs (removes guild commands)
sd- sync id_1 id_2 -> syncs guilds with id 1 and 2"""

@bot.command(name="synccmd")
async def sync(
  ctx: Context, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        print(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1
    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


json = utilities.load_json(assets.jsonfile)
token = json["token"]
bot.run(token)