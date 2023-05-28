from .follow import FollowCog


async def setup(bot):
    await bot.add_cog(FollowCog(bot))