from discord.ext import commands

from models.db.database import DataBase


class Bot(commands.Bot):
    """
    A subclass of commands.Bot.

    This class adds a db attribute to the bot which is an instance of the DataBase class.
    """

    db: DataBase
