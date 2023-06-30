from .admintoggle import AdminToggle

async def setup(bot):
    await bot.add_cog(AdminToggle(bot))