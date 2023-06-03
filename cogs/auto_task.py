import asyncio
import datetime
from datetime import timedelta
from typing import List, Tuple

from discord.ext import commands

from i18n.translator import translator
from models.bot import Bot
from models.db.tables.event import Event, RecurInterval
from models.embeds import DefaultEmbed


class AutoTask(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.event_queue: List[Tuple[float, Event]] = []

    async def cog_load(self) -> None:
        """
        This function is called when the cog is loaded.

        Returns:
            None
        """
        await self.load_events()

    async def load_events(self) -> None:
        """
        This function loads all the events from the database.

        Returns:
            None
        """
        self.event_queue = []
        events = await self.bot.db.events.get_all()
        for event in events:
            if event.date_time < datetime.datetime.now():
                await self.bot.db.events.delete(event.id)
            else:
                self.bot.loop.create_task(self.schedule_event(event))

    async def schedule_event(self, event: Event) -> None:
        """
        This function schedules an event.

        Args:
            event (Event): The event to schedule.

        Returns:
            None
        """
        time_until_event = event.date_time - datetime.datetime.now()
        await asyncio.sleep(time_until_event.total_seconds())
        await self.notify_user(event)
        if event.recur:
            await self.schedule_recur(event)
        else:
            await self.bot.db.events.delete(event.id)

    async def schedule_recur(self, event: Event) -> None:
        """
        This function schedules a recurring event.

        Args:
            event (Event): The event to schedule.

        Returns:
            None
        """
        if event.recur_interval is RecurInterval.DAILY:
            next_event = event.date_time + timedelta(days=1)
        elif event.recur_interval is RecurInterval.WEEKLY:
            next_event = event.date_time + timedelta(weeks=1)
        elif event.recur_interval is RecurInterval.MONTHLY:
            next_event = event.date_time.replace(month=event.date_time.month + 1)
        elif event.recur_interval is RecurInterval.YEARLY:
            next_event = event.date_time.replace(year=event.date_time.year + 1)
        else:
            raise ValueError("Invalid recur interval")

        await self.bot.db.events.update(
            event.id,
            date_time=next_event,
        )
        event.date_time = next_event
        await self.schedule_event(event)

    async def notify_user(self, event: Event) -> None:
        """
        This function notifies the user that an event is happening soon.

        Args:
            event (Event): The event to notify the user about.

        Returns:
            None
        """
        user = self.bot.get_user(event.user_id)
        if user is None:
            user = await self.bot.fetch_user(event.user_id)

        embed = DefaultEmbed()
        embed.title = translator.translate("en-US", "event_reminder.embed.title")
        embed.description = event.name
        if event.recur:
            embed.set_footer(
                text=f" ({translator.translate('en-US', 'event_reminder.embed.recurring')})"
            )
        
        await user.send(embed=embed, content=user.mention)


async def setup(bot: Bot) -> None:
    """
    This function sets up the AutoTask cog.

    Args:
        bot (Bot): The bot instance.

    Returns:
        None
    """
    await bot.add_cog(AutoTask(bot))
