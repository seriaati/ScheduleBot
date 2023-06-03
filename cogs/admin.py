from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.is_owner()
    @commands.command()
    async def sync(self, ctx: commands.Context) -> None:
        await ctx.send("Syncing...")
        synced = await self.bot.tree.sync()
        await ctx.send(f"Synced {len(synced)} commands.")
    
async def setup(bot: commands.Bot) -> None:
    """
    This function sets up the Admin cog.

    Args:
        bot (commands.Bot): The bot instance.

    Returns:
        None
    """
    await bot.add_cog(Admin(bot))