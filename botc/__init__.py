from .botc import BotCCog

async def setup(bot):
    await bot.add_cog(BotCCog(bot))