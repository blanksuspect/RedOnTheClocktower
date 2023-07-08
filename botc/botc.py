import logging
import discord
import json
from discord import Colour
from redbot.core import Config, commands
from redbot.core import commands, app_commands
from datetime import datetime, timedelta
import asyncio

log = logging.getLogger("red.botc.botc")

class BotCCog(commands.Cog):
    """Adding commands to run a game of Blood on the Clocktower"""

    __version__ = "0.0.1"
    __author__ = "Burnacid"

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=68468174687465121988)
        default_guild = {}
        self.config.register_guild(**default_guild)

        self.deadline = None
        self.dayrunning = False

        pass

    async def is_admin(self, member: discord.Member) -> bool:
        guild = member.guild
        if member == guild.owner:
            return True
        if await self.bot.is_owner(member):
            return True
        if await self.bot.is_admin(member):
            return True
        return False
    
    async def create_storyteller_role(self, guild: discord.Guild) -> bool:
        stGroupId = await self.config.guild(guild).storyteller()
        if stGroupId is not None:
            role = guild.get_role(stGroupId)

            if role is not None:
                return True

        role = await guild.create_role(name="Storyteller", colour=Colour.gold(), hoist=True, mentionable=True, reason="Setup Blood on the Clocktower by Bot")
        await self.config.guild(guild).storyteller.set(role.id)
        return True
    
    async def create_day(self, guild: discord.Guild) -> bool:
        with open('/data/cogs/CogManager/cogs/botc/townlayout.json') as f:
            j = json.load(f)

        dayCategory = await self.config.guild(guild).daycategory()
        storyteller = await self.config.guild(guild).storyteller()
        storytellerRole = guild.get_role(storyteller)

        if dayCategory is not None:
            dayCategoryChannel = guild.get_channel(dayCategory)
            if dayCategoryChannel is not None:
                # Cleanup old day category
                for c in dayCategoryChannel.channels:
                    await c.delete(reason="Removing old setup")
                
                await dayCategoryChannel.delete(reason="Removing old setup")

        overwrites = {
            storytellerRole: discord.PermissionOverwrite(view_channel=True, move_members=True, mute_members=True)
        }
        
        dayCategoryChannel = await guild.create_category_channel(name="🌞 Day BOTC",overwrites=overwrites)
        await self.config.guild(guild).daycategory.set(dayCategoryChannel.id)

        for t in j['DAY']['TextChannels']:
            await dayCategoryChannel.create_text_channel(t)

        for v in j['DAY']['VoiceChannels']:
            log.info(v)
            await dayCategoryChannel.create_voice_channel(v)

    async def create_night(self, guild: discord.Guild) -> bool:
        with open('/data/cogs/CogManager/cogs/botc/townlayout.json') as f:
            j = json.load(f)

        nightCategory = await self.config.guild(guild).nightcategory()
        storyteller = await self.config.guild(guild).storyteller()
        storytellerRole = guild.get_role(storyteller)

        if nightCategory is not None:
            nightCategoryChannel = guild.get_channel(nightCategory)
            if nightCategoryChannel is not None:
                # Cleanup old day category
                for c in nightCategoryChannel.channels:
                    await c.delete(reason="Removing old setup")
                
                await nightCategoryChannel.delete(reason="Removing old setup")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            storytellerRole: discord.PermissionOverwrite(view_channel=True, move_members=True, mute_members=True)
        }
        
        nightCategoryChannel = await guild.create_category_channel(name="🌙 Night BOTC ✨",overwrites=overwrites)
        await self.config.guild(guild).nightcategory.set(nightCategoryChannel.id)

        for v in j['NIGHT']['VoiceChannels']:
            log.info(v)
            await nightCategoryChannel.create_voice_channel(v)        

    async def move_townsquare(self, ctx: commands.Context, dayCategoryChannel: discord.CategoryChannel):
        dayChannels = dayCategoryChannel.voice_channels
        townSquareChannels = dayChannels[0]
        del dayChannels[0]

        for v in dayChannels:
            for m in v.members:
                #Skip players with a ! in front of their name
                if m.display_name.startswith("!"):
                    continue
                
                await m.move_to(townSquareChannels)
        
        await ctx.send(f"Welcome back!")

    @commands.group(name="botc")
    @commands.guild_only()
    @commands.admin()
    async def botc(self, ctx: commands.Context):
        """Commands for setup Blood on the Clocktower"""
        pass

    @botc.command(name="setup")
    @commands.guild_only()
    @commands.admin()
    async def botc_setup(self, ctx: commands.Context):
        """Setup Blood on the Clocktower Channels & Roles"""

        guild = ctx.guild

        try:
            # Create ST role
            await self.create_storyteller_role(guild)

            # Create Day channels
            await self.create_day(guild)

            # Create Night channels
            await self.create_night(guild)

        except Exception as e:
            log.error(e)

        pass

    @botc.group(name="config")
    @commands.guild_only()
    @commands.admin()
    async def config(self, ctx: commands.Context):
        """Manual configure stuff for BotC"""
        pass

    @config.command(name="storyteller")
    @commands.guild_only()
    @commands.admin()
    async def botc_config_storyteller(self, ctx: commands.Context, role: discord.Role):
        """Mark a role for the storyteller"""
        
        await self.config.guild(ctx.guild).storyteller.set(role.id)
        await ctx.send(f"{role.mention} is set as storyteller role", delete_after=60)

    @config.command(name="daychannels")
    @commands.guild_only()
    @commands.admin()
    async def botc_config_daychannels(self, ctx: commands.Context, channel: discord.CategoryChannel):
        """Mark category as day channels"""
        
        await self.config.guild(ctx.guild).daycategory.set(channel.id)
        await ctx.send(f"{channel.mention} is set as day channel category", delete_after=60)

    @config.command(name="nightchannels")
    @commands.guild_only()
    @commands.admin()
    async def botc_config_daychannels(self, ctx: commands.Context, channel: discord.CategoryChannel):
        """Mark category as day channels"""
        
        await self.config.guild(ctx.guild).nightcategory.set(channel.id)
        await ctx.send(f"{channel.mention} is set as night channel category", delete_after=60)

    @commands.hybrid_command()
    @app_commands.guild_only()
    async def night(self, ctx: commands.Context):
        """Enter into the Night Phase for Blood on the Clocktower and move all players to a night cottage"""

        storyteller = await self.config.guild(ctx.guild).storyteller()
        storytellerRole = ctx.author.get_role(storyteller)

        if storytellerRole is None:
            await ctx.send(f"You are not a storyteller!", ephemeral=True)
            return

        dayCategory = await self.config.guild(ctx.guild).daycategory()
        dayCategoryChannel = ctx.guild.get_channel(dayCategory)
        if dayCategoryChannel is None:
            await ctx.send(f"I could not find the townsquere. Something must have been deleted/moved or destroyed!", ephemeral=True)
            return
        
        nightCategory = await self.config.guild(ctx.guild).nightcategory()
        nightCategoryChannel = ctx.guild.get_channel(nightCategory)
        if nightCategoryChannel is None:
            await ctx.send(f"I could not find the night cottages. Something must have been deleted/moved or destroyed!", ephemeral=True)
            return
        
        nightCottages = nightCategoryChannel.voice_channels
        cottageIndex = 0

        await ctx.send(f"Moving players to their cottages. Please wait!", ephemeral=False)

        for v in dayCategoryChannel.voice_channels:
            for m in v.members:
                #Skip players with a ! in front of their name
                if m.display_name.startswith("!"):
                    continue

                #Skip storytellers
                if m.get_role(storyteller) is not None:
                    continue
                
                await m.move_to(nightCottages[cottageIndex])
                cottageIndex += 1


    @commands.hybrid_command()
    @app_commands.guild_only()
    async def day(self, ctx: commands.Context):
        """Enter into the Day Phase for Blood on the Clocktower and move all players to the Town Square"""

        storyteller = await self.config.guild(ctx.guild).storyteller()
        storytellerRole = ctx.author.get_role(storyteller)

        if storytellerRole is None:
            await ctx.send(f"You are not a storyteller!", ephemeral=True)
            return

        dayCategory = await self.config.guild(ctx.guild).daycategory()
        dayCategoryChannel = ctx.guild.get_channel(dayCategory)
        if dayCategoryChannel is None:
            await ctx.send(f"I could not find the townsquere. Something must have been deleted/moved or destroyed!", ephemeral=True)
            return
        
        nightCategory = await self.config.guild(ctx.guild).nightcategory()
        nightCategoryChannel = ctx.guild.get_channel(nightCategory)
        if nightCategoryChannel is None:
            await ctx.send(f"I could not find the night cottages. Something must have been deleted/moved or destroyed!", ephemeral=True)
            return
        
        dayChannels = dayCategoryChannel.voice_channels

        await ctx.send(f"Moving players to the Town Square. Please wait!", ephemeral=False)

        for v in nightCategoryChannel.voice_channels:
            for m in v.members:
                #Skip players with a ! in front of their name
                if m.display_name.startswith("!"):
                    continue
                
                await m.move_to(dayChannels[0])

    @commands.hybrid_command()
    @app_commands.guild_only()
    async def townsquare(self, ctx: commands.Context):
        """Move everyone back to townsquare"""

        storyteller = await self.config.guild(ctx.guild).storyteller()
        storytellerRole = ctx.author.get_role(storyteller)

        if storytellerRole is None:
            await ctx.send(f"You are not a storyteller!", ephemeral=True)
            return

        dayCategory = await self.config.guild(ctx.guild).daycategory()
        dayCategoryChannel = ctx.guild.get_channel(dayCategory)
        if dayCategoryChannel is None:
            await ctx.send(f"I could not find the townsquere. Something must have been deleted/moved or destroyed!", ephemeral=True)
            return
        
        nightCategory = await self.config.guild(ctx.guild).nightcategory()
        nightCategoryChannel = ctx.guild.get_channel(nightCategory)
        if nightCategoryChannel is None:
            await ctx.send(f"I could not find the night cottages. Something must have been deleted/moved or destroyed!", ephemeral=True)
            return
        
        await ctx.send(f"Moving players to the Town Square. Please wait!", ephemeral=False)
        await self.move_townsquare(ctx, dayCategoryChannel)

    @commands.hybrid_command()
    @app_commands.guild_only()
    @app_commands.describe(minutes="Number of minutes for private chats", automatic="Automatic pull people back to town square when time is up?")
    @app_commands.choices(automatic=[
        app_commands.Choice(name='Yes', value=1),
        app_commands.Choice(name='No', value=0)
    ])
    async def startday(self, ctx: commands.Context, minutes: int, automatic: app_commands.Choice[int] = 1):
        """Start the day for private chats with x minutes. By default pulling everyone back to town square"""

        minutes = int(minutes)

        storyteller = await self.config.guild(ctx.guild).storyteller()
        storytellerRole = ctx.author.get_role(storyteller)

        if storytellerRole is None:
            await ctx.send(f"You are not a storyteller!", ephemeral=True)
            return
        
        dayCategory = await self.config.guild(ctx.guild).daycategory()
        dayCategoryChannel = ctx.guild.get_channel(dayCategory)
        if dayCategoryChannel is None:
            await ctx.send(f"I could not find the townsquere. Something must have been deleted/moved or destroyed!", ephemeral=True)
            return
        
        nightCategory = await self.config.guild(ctx.guild).nightcategory()
        nightCategoryChannel = ctx.guild.get_channel(nightCategory)
        if nightCategoryChannel is None:
            await ctx.send(f"I could not find the night cottages. Something must have been deleted/moved or destroyed!", ephemeral=True)
            return

        if self.dayrunning:
            deadlineString = self.deadline.strftime('%d-%m-%Y %H:%M:%S')
            await ctx.send(f"The day has already started and will end at {deadlineString}", ephemeral=True)
            return

        now = datetime.now()
        self.deadline = now + timedelta(minutes = minutes)
        deadlineString = self.deadline.strftime('%d-%m-%Y %H:%M:%S')
        self.dayrunning = True

        await ctx.send(f"The day has started. You have {minutes} minutes for private chats. (Until {deadlineString})", ephemeral=False)

        await asyncio.sleep((minutes - 1) * 60)

        await ctx.send(f"The day will end in 1 minute!")

        await asyncio.sleep(50)

        await ctx.send(f"Back to town square please! (10 seconds)")

        await asyncio.sleep(10)

        if automatic == 1:
            await self.move_townsquare(ctx, dayCategoryChannel)
        
        self.dayrunning = False

    @commands.hybrid_command()
    @app_commands.guild_only()
    @app_commands.describe(member="Who do you want to assign as storyteller?")
    async def storyteller(self, ctx: commands.Context, member: discord.Member = None):
        """Assign/unassign yourself or someone else as storyteller"""

        if ctx.author.voice is None:
            await ctx.send(f"You need to be connected to a voice channel before you can become storyteller", ephemeral=True)
            return

        gameState = await self.config.guild(ctx.guild).gameState()
        if gameState is None:
            gameState = 0

        storyteller = await self.config.guild(ctx.guild).storyteller()
        storytellerRole = ctx.author.get_role(storyteller)

        currentStorytellers = ctx.guild.get_role(storyteller)

        if currentStorytellers is None:
            await ctx.send(f"The storyteller role could not be found anymore!", ephemeral=True)

        # Fetch the current storytellers online
        onlineStorytellers = []
        for s in currentStorytellers.members:
            if s.voice is not None:
                onlineStorytellers.append(s.mention)

        onlineStorytellersString = ", ".join(onlineStorytellers)

        # Assign or remove own role
        if member is None:
            if storytellerRole is None:
                if gameState == 1 and storytellerRole is None and len(onlineStorytellers) > 0:
                    await ctx.send(f"You can't assign yourself as storyteller while the game is running by other storytellers than you. Current storytellers: {onlineStorytellersString}", ephemeral=True)
                    return
                
                await ctx.send(f"{ctx.author.mention} is now storyteller", ephemeral=False)
                await ctx.author.add_roles(currentStorytellers)

            else:
                await ctx.send(f"{ctx.author.mention} is no longer storyteller", ephemeral=False)
                await ctx.author.remove_roles(currentStorytellers)

        else:
            if gameState == 1 and storytellerRole is None and len(onlineStorytellers) > 0:
                await ctx.send(f"You can't assign or remove {member.mention} as storyteller while the game is running by other storytellers than you. Current storytellers: {onlineStorytellersString}", ephemeral=True)
                return

            if member.get_role(storyteller) is None:
                await ctx.send(f"{member.mention} is now storyteller", ephemeral=False)
                await member.add_roles(currentStorytellers)
            else:
                await ctx.send(f"{member.mention} is no longer storyteller", ephemeral=False)
                await member.remove_roles(currentStorytellers)
        pass

    @commands.hybrid_command()
    @app_commands.guild_only()
    async def start(self, ctx: commands.Context,):
        """Start the game of Blood on the Clocktower and locking storytellers"""

        storyteller = await self.config.guild(ctx.guild).storyteller()
        storytellerRole = ctx.author.get_role(storyteller)

        if storytellerRole is None:
            await ctx.send(f"You can't start the game. You are not a storyteller!", ephemeral=True)
            return
        
        gameState = await self.config.guild(ctx.guild).gameState()
        if gameState is None:
            gameState = 0

        if gameState == 1:
            await ctx.send(f"The game is already started.", ephemeral=True)
            return
        
        currentStorytellers = ctx.guild.get_role(storyteller)
        
        # Fetch the current storytellers offline
        onlineStorytellers = []
        for s in currentStorytellers.members:
            if s.voice is not None:
                onlineStorytellers.append(s.mention)

        onlineStorytellersString = ", ".join(onlineStorytellers)
        
        await self.config.guild(ctx.guild).gameState.set(1)
        await ctx.send(f"You started the game of Blood on the Clocktower. No new storytellers can assign themselves. Please stop the game when you are done using /stop! Currently storytelling are: {onlineStorytellersString}. If you are not supposed to be a storyteller please use /storyteller to remove this role for yourself!", ephemeral=False)

        # Fetch the current storytellers offline
        offlineStorytellers = []
        for s in currentStorytellers.members:
            if s.voice is None:
                offlineStorytellers.append(s.mention)
                await s.remove_roles(currentStorytellers)

        if len(offlineStorytellers) > 0:
            offlineStorytellersString = ", ".join(offlineStorytellers)
            await ctx.send(f"Removed {offlineStorytellersString} as storytellers as they are not online")
        
    @commands.hybrid_command()
    @app_commands.guild_only()
    async def stop(self, ctx: commands.Context):
        """Stop the game of Blood on the Clocktower and removing all storytellers"""

        storyteller = await self.config.guild(ctx.guild).storyteller()
        storytellerRole = ctx.author.get_role(storyteller)

        if storytellerRole is None:
            await ctx.send(f"You can't stop the game. You are not a storyteller!", ephemeral=True)
            return
        
        gameState = await self.config.guild(ctx.guild).gameState()

        if gameState is None:
            gameState = 0

        if gameState == 0:
            await ctx.send(f"The game not started.", ephemeral=True)
            return
        
        currentStorytellers = ctx.guild.get_role(storyteller)
        storytellers = []
        for s in currentStorytellers.members:
            storytellers.append(s.mention)
            await s.remove_roles(currentStorytellers)

        storytellersString = ", ".join(storytellers)

        await self.config.guild(ctx.guild).gameState.set(0)
        await ctx.send(f"Blood on the Clocktower game has stopped. Thanks for running. Removed {storytellersString} as storyteller(s)", ephemeral=False)


    @botc.command(name="clean")
    @commands.guild_only()
    @commands.admin()
    async def botc_clean(self, ctx: commands.Context, minutes: int):
        """Set the text channels within the BotC channels to be cleaned automatically"""

        await self.config.guild(ctx.guild).cleanAfterMinutes.set(minutes)

        if minutes <= 0:
            await ctx.channel.send("Cleanup messages from BotC text channel has been disabled")
        else:
            await ctx.channel.send(f"Cleanup messages from BotC text channel has been enabled and set to {minutes} minutes")
        

    @commands.Cog.listener()
    async def on_message(self, message):
        """Checks for messages in monitored channel"""
        
        if message.guild is None:
            return
        
        cleanAfterMinutes = await self.config.guild(message.guild).cleanAfterMinutes()
        if cleanAfterMinutes is None:
            return

        if cleanAfterMinutes <= 0:
            return
        
        channel = message.channel
        dayCategory = await self.config.guild(message.guild).daycategory()
        nightCategory = await self.config.guild(message.guild).nightcategory()
        
        if channel.category_id == dayCategory or channel.category_id == nightCategory:
            await message.delete(delay=(cleanAfterMinutes*60))