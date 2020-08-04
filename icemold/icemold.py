import asyncio
from typing import Any

from redbot.core import commands, Config
from redbot.core import Config, checks, commands, bank
import time

from redbot.core.bot import Red

Cog: Any = getattr(commands, "Cog", object)

class Icemold(Cog):
    """My custom cog"""
    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(
            self, identifier=30195332122266669, force_registration=True
        )
        self.config.register_member(
            toggle=False,
            creditperloop=1000
        )

    @commands.group(autohelp=True)
    @checks.is_owner()
    async def icemoldset(self, ctx):
        """Settings for this icemold"""
        pass

    @icemoldset.command(name="toggle")
    async def icemoldset_toggle(self, ctx: commands.Context, on_off: bool = None):
        """Toggle IceMold for you

        If 'on_off' is not provided, the state will be flipped."""
        target_state = (
            on_off
            if on_off
            else not (await self.config.member(ctx.author).toggle())
        )
        await self.config.member(ctx.author).toggle.set(target_state)
        if target_state:
            await ctx.send("Bond System is now enabled.")
        else:
            await ctx.send("Bond System is now disabled.")

    @icemoldset.command(name="amount")
    async def icemoldset_amount(self, ctx: commands.Context, amount: int):
        """Set amount of icicles per loop"""
        if amount <= 0:
            await ctx.send("Why the fuck would I go into debt for their sorry ass?")
        await self.config.guild(ctx.guild).creditperloop.set(amount)
        await ctx.send("the credit per loop is now " + str(await self.config.guild(ctx.guild).rollprice()))
        await ctx.tick()

    @checks.is_owner()
    @commands.command()
    async def start(self, ctx):
        """passively gain icicles suckers"""
        user = ctx.author
        await self.bot.wait_until_ready()
        while self.config.member(user).toggle():
            await bank.deposit_credits(user, await self.config.member(user).creditperloop())
            await ctx.send("You're gaining money now!")
            await asyncio.sleep(60)