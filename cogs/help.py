import discord
from discord import app_commands
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

async def setup(bot: commands.Bot) -> None:
    """
    This function sets up the Help cog.

    Args:
        bot (commands.Bot): The bot instance.

    Returns:
        None
    """
    await bot.add_cog(Help(bot))