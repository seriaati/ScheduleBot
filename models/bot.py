from typing import Tuple

from discord import app_commands
from discord.app_commands.translator import TranslationContextTypes, locale_str
from discord.enums import Locale
from discord.ext import commands

from i18n.translator import translator
from models.db.database import DataBase


class Bot(commands.Bot):
    """
    A subclass of commands.Bot.

    Attributes:
        db (DataBase): The database.
    """

    db: DataBase
    owner_ids: Tuple[int, ...]


class BotTranslator(app_commands.Translator):
    """
    The translator for the bot.
    """

    async def translate(
        self, string: locale_str, locale: Locale, _: TranslationContextTypes
    ) -> str:
        """
        Translate a string to the specified language.

        Args:
            string (str): The string to translate.
            locale (Locale): The language to translate to.
            _ (TranslationContextTypes): The context of the string.

        Returns:
            str: The translated string.
        """
        try:
            return translator.translate(locale.value, string.extras["context"])
        except KeyError:
            return None
