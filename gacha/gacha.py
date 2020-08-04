import discord
import asyncio
import json
from random import choice, choices

from typing import Any, List

from redbot.core.utils.menus import menu, commands, DEFAULT_CONTROLS
from redbot.core import Config, checks, commands, bank
from redbot.core.data_manager import bundled_data_path, cog_data_path

from redbot.core.bot import Red

Cog: Any = getattr(commands, "Cog", object)

__author__ = "MeltyCoco"
__version__ = "0.0.1"

class Gacha(Cog):
    """Marry shit"""

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(
            self, identifier=31695332122266669, force_registration=True
        )

        self.config.register_user(
            normal=[],
            rare=[],
            sr=[],
            ssr=[],
            ur=[],
            wishlist=[]
        )

        self.config.register_guild(
            toggle=True,
            rollprice=int(100000)
        )

    async def _send_message(channel, message):
        """Sends a message"""

        em = discord.Embed(description=message, color=discord.Color.green())
        await channel.send(embed=em)

    async def _load_card_list(self):
        """reloads the card list"""
        card_data_fp = bundled_data_path(self) / "default" / "cards.json"
        with card_data_fp.open() as json_data:
            self.card_data = json.load(json_data)

    async def _grab_random_rarity(self, amount: int):
        """grabs a random rarity"""
        # EVERYTIME YOU ADD A RARITY, BE SURE TO ADD IT HERE AND WEIGHT IT
        raritylist = ["normal", "rare", "super rare", "super super rare", "ultra rare"]
        raritygrabbed = choices(raritylist, weights=[40, 50, 8, 2, 1], k=amount)
        return raritygrabbed

    async def _create_inventory_list(self, cardlist: [], rarity: str):
        """Takes in one of the inventories' list and creates a list of it"""
        allcard = []
        for x in range(0, len(cardlist)):
            tempcard = cardlist[x]
            tempnormal = await self._create_single_page(tempcard, rarity)
            allcard.append(tempnormal)
        return allcard

    async def _create_card_list(self,cardlist: [], amount: int, rarity: str):
        """Creates a list of all card from a card list as a page"""
        pagelist = []
        for x in range(0, amount):
            # Grabs a random card of the rarity grabbed and then creates the embed card for that card
            # ERROR HERE DUE TO NOT GRABBING THE SPECIFIC CARD'S LOCATION LMAO
            tempcard = cardlist[x]
            embed = discord.Embed(title=tempcard["name"], description=tempcard["series"])
            embed.set_thumbnail(url=tempcard["image"])
            embed.add_field(name="Rarity", value=rarity, inline=False)
            embed.add_field(name="Birthday", value=tempcard["birthday"], inline=False)
            embed.add_field(name="Quote", value=tempcard["quote"], inline=False)
            embed.add_field(name="page", value=str(x + 1) + " out of " + str(amount), inline=False),
            embed.set_footer(text="I know you want another gacha hit")
            pagelist.append(embed)
        return pagelist

    async def _create_single_page(self,card: [], rarity: str):
        """Creates a page of a single card"""
        # Grabs a random card of the rarity grabbed and then creates the embed card for that card
        # ERROR HERE DUE TO NOT GRABBING THE SPECIFIC CARD'S LOCATION LMAO
        tempcard = card
        embed = discord.Embed(title=tempcard["name"], description=tempcard["series"])
        embed.set_thumbnail(url=tempcard["image"])
        embed.add_field(name="Rarity", value=rarity, inline=False)
        embed.add_field(name="Birthday", value=tempcard["birthday"], inline=False)
        embed.add_field(name="Quote", value=tempcard["quote"], inline=False)
        embed.set_footer(text="I know you want another gacha hit")
        return embed

    # Takes in a card and a rarity string
    # Will add the card into the proper list of rarities
    async def _add_card_to_inventory(self, ctx: commands.Context, card: [], rarity: str):
        normal = await self.config.user(ctx.author).normal()
        rare = await self.config.user(ctx.author).rare()
        sr = await self.config.user(ctx.author).sr()
        ssr = await self.config.user(ctx.author).ssr()
        ur = await self.config.user(ctx.author).ur()
        if rarity == "normal":
            normal.append(card)
            await self.config.user(ctx.author).normal.set(normal)
        elif rarity == "rare":
            rare.append(card)
            await self.config.user(ctx.author).rare.set(rare)
        elif rarity == "super rare":
            sr.append(card)
            await self.config.user(ctx.author).sr.set(sr)
        elif rarity == "super super rare":
            ssr.append(card)
            await self.config.user(ctx.author).ssr.set(ssr)
        elif rarity == "ultra rare":
            ur.append(card)
            await self.config.user(ctx.author).ur.set(ur)
        else:
            await ctx.send("There's an issue with the rarity!")

    @commands.group(autohelp=True)
    @checks.admin_or_permissions(manage_guild=True)
    async def gachaset(self, ctx):
        """Settings for this gacha"""
        pass

    @gachaset.command(name="toggle")
    async def gachaset_toggle(self, ctx: commands.Context, on_off: bool = None):
        """Toggle Bond System for server

        If 'on_off' is not provided, the state will be flipped."""
        target_state = (
            on_off
            if on_off
            else not (await self.config.guild(ctx.guild).toggle())
        )
        await self.config.guild(ctx.guild).toggle.set(target_state)
        if target_state:
            await ctx.send("Bond System is now enabled.")
        else:
            await ctx.send("Bond System is now disabled.")

    @checks.is_owner()
    @gachaset.command(name="rollprice")
    async def gachaset_rollprice(self, ctx: commands.Context, price: int):
        """Set the price for rolling"""

        if price <= 0:
            await ctx.send("Why the fuck would I go into debt for their sorry ass?")
        await self.config.guild(ctx.guild).rollprice.set(price)
        await ctx.send("the price is now " + str(await self.config.guild(ctx.guild).rollprice()))
        await ctx.tick()

        #        @commands.command()
        #        async def wish(self, ctx: commands.Context, card: card.name = None):
        #            """Add a card to your wishlist"""

        #        if not await self.config.guild(ctx.guild).toggle():
        #            return await ctx.send("Bitch, you can't gacha in this server")
        #        if not card:
        #            await self.configmember(ctx.quthor).wishlist.set(None)

    @commands.group(autohelp=True)
    async def card(self,ctx):
        """View cards"""
        pass

    @card.command(name="inventory")
    async def card_inventory(self, ctx: commands.Context, topage: int = 0, reverse: bool=True):
        """View your inventory, add a number to jump to that page or say reverse to reverse!"""
        # Make each list easier to access
        normal = await self.config.user(ctx.author).normal()
        rare = await self.config.user(ctx.author).rare()
        sr = await self.config.user(ctx.author).sr()
        ssr = await self.config.user(ctx.author).ssr()
        ur = await self.config.user(ctx.author).ur()
        raritylist = ["normal", "rare", "super rare", "super super rare", "ultra rare"]
        currentinv = []
        totalcards = 0

        currentinv.append(normal)
        currentinv.append(rare)
        currentinv.append(sr)
        currentinv.append(ssr)
        currentinv.append(ur)

        for x in range(0, len(raritylist)):
            totalcards += len(currentinv[x])

        allcard=[]
        titlepage = discord.Embed(title=f"{ctx.author.name}'s cards")
        titlepage.set_thumbnail(url="https://i.imgur.com/JDTZ7XO.jpg?1")
        titlepage.add_field(name="Total cards", value= str(str(totalcards)), inline=False)
        titlepage.add_field(name="Total normal", value= str(len(normal)), inline=False)
        titlepage.add_field(name="Total rare", value= str(len(rare)), inline=False)
        titlepage.add_field(name="Total super rare", value= str(len(sr)), inline=False)
        titlepage.add_field(name="Total super super rare", value= str(len(ssr)), inline=False)
        titlepage.add_field(name="Total ultra rare", value= str(len(ur)), inline=False)
        titlepage.set_footer(text="Use the arrows to navigate")
        allcard.append(titlepage)

        # puts all of the cards into one list
        for x in range(0,len(raritylist)):
            templist = await self._create_inventory_list(currentinv[x], raritylist[x])
            allcard += templist

        await menu(ctx, pages=allcard, controls=DEFAULT_CONTROLS, message=None, page=topage, timeout=60)

    @card.command(name="inventorywipe")
    async def cards_ivnwipe(self, ctx: commands.Context):
        """wipes the caller's inventory -For dev purpose"""
        await self.config.user(ctx.author).normal.set([])
        await self.config.user(ctx.author).rare.set([])
        await self.config.user(ctx.author).sr.set([])
        await self.config.user(ctx.author).ssr.set([])
        await self.config.user(ctx.author).ur.set([])
        await ctx.send("inventory wiped!")

    @commands.group(autohelp=True)
    async def gacha(self, ctx):
        """Perform actions for gachaing"""
        pass

    @gacha.command(name="roll")
    async def gacha_roll(self, ctx: commands.Context, amount: int = 1):
        """pulls a card from the current card list"""
        await self._load_card_list()
        author = ctx.author
        totalcost = await self.config.guild(ctx.guild).rollprice()
        totalcost *= amount

        if bank.can_spend(author, totalcost):
            # every ten rolls, give grant 1 extra roll!
            if (int(amount / 10) >= 1):
                amount += int(amount / 10)

            raritygrabbed = await self._grab_random_rarity(amount)

            # Start creating pages for the embed command
            allcard = []
            titlepage = discord.Embed(title=f"{author.name}'s rolls")
            titlepage.set_thumbnail(url="https://i.imgur.com/JDTZ7XO.jpg?1")
            titlepage.add_field(name="Total cards", value=str(amount), inline=False)
            titlepage.add_field(name="Total cost", value=totalcost, inline=False)
            titlepage.set_footer(text="Use the arrows to navigate")
            allcard.append(titlepage)

            await bank.withdraw_credits(author, totalcost)

            rawcardlist = []
            for x in range(0, amount):
                raritystring = raritygrabbed[x]
                # grabs a rarity from the rarity list above
                card_options = self.card_data[raritystring]
                cardrolled = choice(card_options)
                rawcardlist.append(cardrolled)
                await self._add_card_to_inventory(ctx, cardrolled, raritystring)
                temppage = await self._create_single_page(cardrolled, raritystring)
                allcard.append(temppage)
            # Print out the pages as a menu (pages doesn't work for some reason)
            await menu(ctx, pages=allcard, controls=DEFAULT_CONTROLS, message=None, page=0, timeout=60)
        else:
            await ctx.send("You don't have enough " + await bank.get_currency_name(ctx.guild) + "! You would need " + str(totalcost) + await bank.get_currency_name(ctx.guild) + "!")