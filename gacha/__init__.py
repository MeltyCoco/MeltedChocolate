from .gacha import Gacha


async def setup(bot):
    bot.add_cog(Gacha(bot))