import logging
import os
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

from models.bot import Bot, BotTranslator
from models.db.database import DataBase


class ScheduleBot(Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=intents,
            activity=discord.Game(name="/remind"),
            owner_ids=(410036441129943050, 260083371819008000, 274853284764975104),
        )
        self.db = DataBase()

    async def setup_hook(self) -> None:
        """
        Set up the bot.

        This method sets up logging, loads the jishaku extension and loads all cogs in the 'cogs' folder.

        Returns:
            None
        """
        # setup logging
        self.setup_logging()
        logging.info("[Bot]Starting bot...")

        # start the database
        await self.db.start()
        
        # setup translator
        await self.tree.set_translator(BotTranslator())

        # load jishaku
        await self.load_extension("jishaku")

        # load cogs in cogs folder
        await self.load_cogs()

    def setup_logging(self) -> None:
        """
        Set up logging for the bot.

        This function sets up basic logging to a file named "schedule_bot.log" and to the console.

        Returns:
            None
        """
        # setup basic logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%y-%m-%d %H:%M:%S",
            filename="schedule_bot.log",
            filemode="w",
        )

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter("%(levelname)s %(name)s %(message)s")
        console.setFormatter(formatter)
        logging.getLogger("").addHandler(console)

    async def load_cogs(self) -> None:
        """
        Load all cogs in the 'cogs' folder.

        This method iterates over all Python files in the 'cogs' folder and attempts to load them as extensions.
        If a file fails to load, an error message is logged.

        Returns:
            None
        """
        for cog in Path("cogs").glob("*.py"):
            try:
                await self.load_extension(f"cogs.{cog.stem}")
            except Exception as e:  # skipcq: PYL-W0703
                logging.error(f"[Bot]Failed to load cog {cog.stem}: {e}", exc_info=True)
            else:
                logging.info(f"[Bot]Loaded cog {cog.stem}")

    async def on_ready(self) -> None:
        """
        This method is called when the bot is ready.

        This method logs the bot's name and ID.

        Returns:
            None
        """
        assert self.user
        logging.info(f"[Bot]Logged in as {self.user.name} ({self.user.id})")

    async def on_message(self, message: discord.Message) -> None:
        """
        This method is called when the bot receives a message.

        This method ignores messages from bots and messages that do not start with the prefix.

        Args:
            message (discord.Message): The message that was received.

        Returns:
            None
        """
        if self.user and message.author.id == self.user.id:
            return
        await self.process_commands(message)

    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        """
        This method is called when a command raises an error.

        This method logs the error and sends a message to the user.

        Args:
            ctx (commands.Context): The context of the command.
            error (commands.CommandError): The error that was raised.

        Returns:
            None
        """
        logging.error(f"[Bot]Error in command {ctx.command}: {error}")
        await ctx.send(f"An error occurred: {error}")

    async def close(self) -> None:
        """
        This method is called when the bot is closed.

        This method closes the database connection and logs the event.

        Returns:
            None
        """
        await self.db.close()
        await super().close()
        logging.info("[Bot]Closed bot")


bot = ScheduleBot()


@bot.listen()
async def on_message_edit(before: discord.Message, after: discord.Message) -> None:
    """
    This function is called when a message is edited.

    This function processes commands in the edited message if the author is a bot owner.

    Args:
        before (discord.Message): The message before it was edited.
        after (discord.Message): The message after it was edited.

    Returns:
        None
    """
    if before.content == after.content or not any(
        before.author.id == id for id in bot.owner_ids
    ):
        return
    await bot.process_commands(after)


load_dotenv()
token = os.getenv("TOKEN")
if token is None:
    raise ValueError("TOKEN environment variable not set")
bot.run(token)