import logging
import discord
from redbot.core import Config, commands
from redbot.core import commands

log = logging.getLogger("red.botc.admintoggle")

class AdminToggle(commands.Cog):
    """Allows a group of users to toggle on or off their admin role"""

    __version__ = "0.0.1"
    __author__ = "Burnacid"

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=68468174687465121991)
        default_guild = {}
        self.config.register_guild(**default_guild)

        pass

    @commands.group(name="admintoggle")
    @commands.guild_only()
    @commands.admin()
    async def admintoggle(self, ctx: commands.Context):
        """Commands for Admin Toggle settings"""
        
        pass

    @admintoggle.command(name="adminrole")
    @commands.guild_only()
    @commands.admin()
    async def adminrole(self, ctx: commands.Context, role: discord.Role):
        """Define the admin role"""

        await self.config.guild(ctx.guild).adminrole.set(role.id)
        await ctx.send(f"{role.mention} is set to the toggle admin role", delete_after=60, allowed_mentions=None)

        pass

    @admintoggle.command(name="role")
    @commands.guild_only()
    @commands.admin()
    async def role(self, ctx: commands.Context, role: discord.Role):
        """Which role is allowed to toggle to admin role"""

        await self.config.guild(ctx.guild).role.set(role.id)
        await ctx.send(f"{role.mention} is set to the role allowed to use /toggleadmin", delete_after=60, allowed_mentions=None)

        pass

    # @admintoggle.group(name="users")
    # @commands.guild_only()
    # @commands.admin()
    # async def users(self, ctx: commands.Context):
    #     """Manage specific users that are allowed to use toggle admin"""

    #     pass

    @commands.hybrid_command(name="toggleadmin")
    async def toggleadmin(self, ctx: commands.Context):
        """Toggle my admin ability on or off"""

        role = await self.config.guild(ctx.guild).role()
        if ctx.author.get_role(role) is None:
            await ctx.send("Nice Try. You don't have that permission!", ephemeral=True)
            return

        adminroleid = await self.config.guild(ctx.guild).adminrole()

        if adminroleid is None:
            await ctx.send("There is no admin role set. Please use `[p]admintoggle adminrole` to set one", ephemeral=True)
            return
        
        adminrole = ctx.guild.get_role(adminroleid)

        if adminrole is None:
            await ctx.send("The admin role set doesn't exist anymore", ephemeral=True)
            return
        
        membership = ctx.author.get_role(adminroleid)
        
        if membership is None:
            await ctx.author.add_roles(adminrole, reason="Used toggleadmin")
            await ctx.send("You admin role is toggled on", ephemeral=True)
        else:
            await ctx.author.remove_roles(adminrole, reason="Used toggleadmin")
            await ctx.send("You admin role is toggled off", ephemeral=True)

        pass