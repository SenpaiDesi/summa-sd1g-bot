

import asyncio
import re
import sqlite3
import time
import assets
import aiosqlite
import discord
import discord.errors
import utilities
from discord.ext import commands
from discord.ext.commands.errors import MissingPermissions
from gpiozero import CPUTemperature

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


def log_counter():
    db = sqlite3.connect("./database.db")
    cur = db.cursor()
    cur.execute("SELECT COUNT (*) FROM moderationLogs")
    global new_case
    result = cur.fetchone()
    new_case = result[0] + 1
    return new_case


def log_converter(type):
    global newtype
    if type == 1:
        newtype = "warn"
        return newtype
    elif type == 2:
        newtype = "mute"
        return newtype
    elif type == 3:
        newtype = "unmute"
        return newtype
    elif type == 4:
        newtype = "kick"
        return newtype
    elif type == 5:
        newtype = "softban"
        return newtype
    elif type == 6:
        newtype = "ban"
        return newtype
    elif type == 7:
        newtype = "unban"
        return newtype


class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k]*float(v)
            except KeyError:
                raise commands.BadArgument("{} is an invalid time-key! h/m/s/d are valid!".format(k))
            except ValueError:
                raise commands.BadArgument("{} is not a number!".format(v))
        return time


class moderation(commands.Cog):
    """Moderation commands for people who do not behave."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        database = await utilities.connectdb(assets.Database_file)
        await database.execute("CREATE TABLE IF NOT EXISTS moderationLogs (logid INTEGER PRIMARY KEY, guildid int, moderationLogTypes int, userid int, moduserid int, content varchar, duration int)")
        await database.commit()
        time.sleep(2)
        try:
            await database.close()
        except ConnectionError:
            print("Closed log db")
            pass

    @commands.command(name='kick', aliases=['k', 'kic'])
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kicks an user, Format: @user Reason for kick"""
        database = await utilities.connectdb(assets.Database_file)
        await ctx.channel.purge(limit=1)
        try:
            log_counter()
            database.execute("INSERT OR IGNORE INTO moderationLogs (logid, guildid, moderationLogTypes, userid, moduserid, content, duration) VALUES(?, ?, ?, ?, ?, ?)", (new_case, ctx.guild.id, 4, member.id, ctx.author.id, reason, "0"))
            await database.commit()
            await asyncio.sleep(2)
            await database.close()
        except aiosqlite.DatabaseError as e:
            print(e)
            try:
                await member.kick(reason=reason)
                await ctx.send(f"✅Kicked {member.name}#{member.discriminator}")
            except MissingPermissions:
                return await ctx.send("You do not have the right permission to kick this user.")

    @commands.command(name='ban', aliases=['b', 'ba'])
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Bans an user. Formaat: @user reden voor verbanning"""
        database = await utilities.connectdb(assets.Database_file)
        await ctx.channel.purge(limit=1)
        try:
            await member.ban(reason=reason)
        except MissingPermissions:
            await ctx.send("Je hebt geen permissies om dit te doen")
        try:
            log_counter()
            await database.execute("INSERT OR IGNORE INTO moderationLogs (logid, guildid, moderationLogTypes, userid, moduserid, content, duration) VALUES (?, ?, ?, ?, ?, ?,?)", (new_case, ctx.guild.id, 6, member.id, ctx.author.id, reason, "0"))
            await database.commit()
            await asyncio.sleep(2)
            await database.close()
        except sqlite3.Connection.Error as e:
            print(f"Connection Closed {e}\n")
            pass
        await ctx.send(f"Logged and Banned ✅ {member}")
        try:
            member.send(f"Hey {member.display_name} You got banned in **{ctx.guild.name}** for: \n**{reason}**")
        except discord.errors.Forbidden:
            return await ctx.send(f"❎Failed to dm {member.name}#{member.discriminator} ")

    @commands.command(name='unban', aliases=['ub', 'unba'])
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member, *, reason=None):
        """Unbans an user from the server. Format: username#0000"""
        database = await utilities.connectdb(assets.Database_file)
        await ctx.channel.purge(limit=1)
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'Unbanned {user.mention}')
                try:
                    log_counter()
                    cur = database.cursor()
                    await database.execute("INSERT OR IGNORE INTO moderationLogs (logid, guildid, moderationLogTypes, userid, moduserid, content, duration) VALUES (?, ?, ?, ?, ?, ?, ?)", (new_case, ctx.guild.id, 7,  member.id, ctx.author.id, reason, "0"))
                    await database.commit()
                    await asyncio.sleep(2)
                    await cur.close()
                    await database.close()
                except sqlite3.Connection.Error:
                    print("Db closed")
                    pass
            return

    @commands.command(name='clear', aliases=['Clear', 'Clr'])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount=200):
        """Clears the channel by given amount. Max of 200"""
        await ctx.channel.purge(limit=amount)
        await ctx.send("Channel cleared!")
        time.sleep(1)
        await ctx.channel.purge(limit=1)

    @commands.command(name='mute', aliases=['Mute', "MUTE"])
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member: discord.Member, time: TimeConverter = None, *, reason=None):
        """Mute an  user. Format @user time(optional, 1h, 1d etc) Reason for mute"""
        database = await utilities.connectdb(assets.Database_file)
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        role_to_remove = []
        log_counter()
        if not role:
            await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(role, speak=False, send_messages=False, read_message_history=True, read_messages=False)
        try:
            if member is not None:
                if time is not None:
                    await member.edit(roles=[])
                    await member.add_roles(role)
                    await database.execute("INSERT INTO moderationLogs (logid, guildid, moderationLogTypes, userid, moduserid, content, duration) VALUES(?, ?, ?, ?, ?, ?, ?)", (new_case, ctx.guild.id, 2, member.id, ctx.author.id, reason, time))
                    await database.commit()
                    await asyncio.sleep(2)
                    await database.close()
                    utilities.create_simple_embed("Muted", discord.color.Blue(), f"Muted {member.display_name}", f"✅Muted user {member.name}#{member.discriminator} for **{reason}**")
                    try:
                        await member.send(f"je bent gemute in **{ctx.guild.name}** voor {reason} en duurt {time}.")
                    except discord.errors.Forbidden:
                        return await ctx.send(f"Logged mute, Kon de user geen dm sturen <@{member.id}>")
                    await asyncio.sleep(time)
                    await member.remove_roles(role)
                else:
                    await member.edit(roles=[])
                    await member.add_roles(role)
                    await database.execute("INSERT INTO moderationLogs (logid, guildid, moderationLogTypes, userid, moduserid, content, duration) VALUES(?, ?, ?, ?, ?, ?, ?)", (new_case, ctx.guild.id, 2, member.id, ctx.author.id, reason, time))
                    await database.commit()
                    await asyncio.sleep(2)
                    await database.close()
                    utilities.create_simple_embed("Muted", discord.color.Blue(), f"Muted {member.display_name}", f"✅Muted user {member.name}#{member.discriminator} voor **{reason}**")
                    try:
                        await member.send(f"Je bent gemute in **{ctx.guild.name}** voor {reason} en is zonder tijd.")
                    except discord.errors.Forbidden:
                        return await ctx.send(f"Logged mute, kon ze geen bericht sturen. <@{member.id}>")
            else:
                if member == ctx.author:
                    return await ctx.send("je kunt jezelf niet muten.")
                elif member == self.bot.user:
                    return await ctx.send("Sorry je kunt mij niet muten.")
        except discord.errors.Forbidden:
            return await ctx.send("je kunt deze user niet muten omdat zijn roles hoger zijn als die van jou.")



    @commands.command(name='ping', aliases=['latency', 'LATENCY', 'PING', 'p'])
    @commands.has_permissions(add_reactions=True)
    async def ping(self, ctx):
        """Check de bot zijn latency."""
        await ctx.send('Pong! `{0} ms `'.format(round(self.bot.latency * 1000)))

    @commands.command(name='warn', aliases=['WARN', 'Warn'])
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member = None, *, reason=None):
        """Waarschuwd een user. Format: @user reason for warn"""
        database = await utilities.connectdb(assets.Database_file)
        if member is not None:
            if reason is not None:
                log_counter()
                await database.execute("INSERT INTO moderationLogs (logid, guildid, moderationLogTypes, userid, moduserid, content, duration) VALUES (?, ?, ?, ?, ?, ?,?)", (new_case, ctx.guild.id, 1, member.id, ctx.author.id, reason, "0"))
                await database.commit()
                await asyncio.sleep(2)
                await database.close()
                try:
                    await member.send(f"je bent gewaarschuwd in {ctx.guild.name} voor {reason}.")
                    await ctx.send(f"✅ user {member.display_name} gewaarschuwd!")
                except discord.errors.Forbidden:
                    return await ctx.send(f"Waarschuwing gelogd voor {member.name}#{member.discriminator}, Ik kon ze geen dm sturen.")

    @commands.command(name='modlogs', aliases=['MODLOGS', 'Modlogs', 'logs', 'Logs', 'LOGS'])
    @commands.has_permissions(manage_messages=True)
    async def modlogs(self, ctx, member: discord.Member = None):
        """Laat de logs van een user zien.. Format: @user """
        database = await utilities.connectdb(assets.Database_file)
        index = 0
        embed = discord.Embed(title=f"logs voor: ({member.id}){member.name}#{member.discriminator}", description="___ ___", color=discord.Color.blue())
        msg = await ctx.send(embed=embed)
        if member is not None:
            try:
                async with database.execute('SELECT logid, moderationLogTypes, moduserid, content, duration FROM moderationLogs WHERE guildid = ? AND userid = ?', (ctx.guild.id, member.id)) as cursor:
                    async for entry in cursor:
                        logid, moderationLogTypes, moduserid, content, duration = entry
                        Moderator = self.bot.get_user(moduserid)
                        type = log_converter(moderationLogTypes)
                        if duration == 0:
                            embed.add_field(name=f"**Case {logid}**", value=f"**User:**{member.name}#{member.discriminator}\n**Type:**{type}\n**Admin:**{Moderator.name}#{Moderator.discriminator}\n**Reason:**{content}", inline=False)
                        else:
                            embed.add_field(name=f"**Case {logid}**", value=f"**User:**{member.name}#{member.discriminator}\n**Type:**{type}\n**Admin:**{Moderator.name}#{Moderator.discriminator}\n**Reason:**{content}\n**Duration:**{duration}", inline=False)
            except Exception as e:
                return await ctx.send(e)
        await msg.edit(embed=embed)
        await asyncio.sleep(2)
        await database.close()

    @commands.command(name='delwarn')
    @commands.has_permissions(manage_messages=True)
    async def delwarn(self, ctx, caseno=None):
        """Verwijderd een log van een user. Format: delwarn case_Number"""
        if caseno is not None:
            database = await utilities.connectdb(assets.Database_file)
            await database.execute("DELETE FROM moderationLogs WHERE logid = ?", (caseno))
            await database.commit()
            await asyncio.sleep(2)
            await database.close()
            await ctx.send(f"✅Deleted {caseno}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(moderation(bot))