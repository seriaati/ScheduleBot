import datetime
import logging
from typing import List, Optional

import discord
import parsedatetime
from discord import app_commands
from discord.app_commands import locale_str as _T
from discord.ext import commands
from pytz import timezone

from i18n.translator import translator
from models.bot import Bot
from models.db.tables.event import Event, RecurInterval
from models.embeds import DefaultEmbed


class Schedule(commands.GroupCog, name="s"):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name=_T("add", context="commands.add.name"),
        description=_T("Schedule a new event", context="commands.add.description"),
    )
    @app_commands.rename(
        name=_T("name", context="commands.add.params.name.name"),
        when=_T("when", context="commands.add.params.when.name"),
        recur_interval=_T(
            "recur_interval", context="commands.add.params.recur_interval.name"
        ),
    )
    @app_commands.describe(
        name=_T("name", context="commands.add.params.name.description"),
        when=_T("when", context="commands.add.params.when.description"),
        recur_interval=_T(
            "recur_interval", context="commands.add.params.recur_interval.description"
        ),
    )
    @app_commands.choices(
        recur_interval=[
            app_commands.Choice(
                name=_T(
                    "Daily", context="commands.add.params.recur_interval.choices.daily"
                ),
                value=1,
            ),
            app_commands.Choice(
                name=_T(
                    "Weekly",
                    context="commands.add.params.recur_interval.choices.weekly",
                ),
                value=2,
            ),
            app_commands.Choice(
                name=_T(
                    "Monthly",
                    context="commands.add.params.recur_interval.choices.monthly",
                ),
                value=3,
            ),
            app_commands.Choice(
                name=_T(
                    "Yearly",
                    context="commands.add.params.recur_interval.choices.yearly",
                ),
                value=4,
            ),
        ],
    )
    async def add(
        self,
        i: discord.Interaction,
        name: str,
        when: str,
        recur_interval: Optional[int] = None,
    ) -> None:
        converted_interval = RecurInterval(recur_interval) if recur_interval else None
        cal = parsedatetime.Calendar()
        datetime_obj, _ = cal.parseDT(
            datetimeString=when, tzinfo=timezone("Asia/Taipei")
        )
        event = Event(
            user_id=i.user.id,
            name=name,
            when=datetime_obj,
            recur=recur_interval is not None,
            recur_interval=converted_interval,
        )
        logging.info(f"[{i.user.id}] Adding event: {event}")
        await self.bot.db.events.add(event)

        lang = i.locale.value
        embed = DefaultEmbed()
        embed.title = translator.translate(lang, "commands.add.embed.title")
        embed.add_field(
            name=translator.translate(lang, "commands.add.embed.fields.name.name"),
            value=event.name,
            inline=False,
        )
        embed.add_field(
            name=translator.translate(lang, "commands.add.embed.fields.when.name"),
            value=f"{discord.utils.format_dt(event.when)}/{discord.utils.format_dt(event.when, 'R')}",
            inline=False,
        )
        embed.add_field(
            name=translator.translate(lang, "commands.add.embed.fields.recur.name"),
            value=translator.translate(
                lang,
                f"commands.add.embed.fields.recur.values.{'yes' if event.recur else 'no'}",
            ),
            inline=False,
        )
        if event.recur_interval:
            embed.add_field(
                name=translator.translate(
                    lang, "commands.add.embed.fields.recur_interval.name"
                ),
                value=translator.translate(
                    lang,
                    f"commands.add.embed.fields.recur_interval.values.{event.recur_interval.value}",
                ),
                inline=False,
            )
        embed.set_author(name=i.user.display_name, icon_url=i.user.display_avatar.url)
        await i.response.send_message(embed=embed)

        now = datetime.datetime.now(tz=timezone("Asia/Taipei"))
        if event.when - now < datetime.timedelta(hours=12):
            cog = self.bot.cogs["AutoTask"]
            self.bot.loop.create_task(cog.schedule_event(event))

    @app_commands.command(
        name=_T("list", context="commands.list.name"),
        description=_T(
            "List the most recent 10 scheduled events",
            context="commands.list.description",
        ),
    )
    async def list(self, i: discord.Interaction) -> None:
        events = await self.bot.db.events.get_all_of_user(i.user.id)
        lang = i.locale.value
        embed = DefaultEmbed()
        embed.title = translator.translate(lang, "commands.list.embed.title")
        for event in events[:10]:
            embed.add_field(
                name=event.name,
                value=f"- {discord.utils.format_dt(event.when)} ({discord.utils.format_dt(event.when, 'R')})\n- ID: {event.id}",
                inline=False,
            )
        embed.set_author(name=i.user.display_name, icon_url=i.user.display_avatar.url)
        embed.set_footer(
            text=translator.translate(lang, "commands.list.embed.footer").format(
                total=len(events)
            )
        )
        await i.response.send_message(embed=embed)

    @app_commands.command(
        name=_T("delete", context="commands.delete.name"),
        description=_T(
            "Delete a scheduled event",
            context="commands.delete.description",
        ),
    )
    @app_commands.rename(event=_T("event", context="commands.delete.params.event.name"))
    @app_commands.describe(event=_T("event", context="commands.delete.params.event.description"))
    async def delete(self, i: discord.Interaction, event: int) -> None:
        await self.bot.db.events.delete(event)
        lang = i.locale.value
        embed = DefaultEmbed()
        embed.title = translator.translate(lang, "commands.delete.embed.title")
        embed.set_footer(
            text=translator.translate(lang, "commands.delete.embed.footer")
        )
        embed.set_author(name=i.user.display_name, icon_url=i.user.display_avatar.url)
        await i.response.send_message(embed=embed)
    
    @delete.autocomplete("event")
    async def delete_autocomplete_event(
        self, i: discord.Interaction, current: str
    ) -> List[app_commands.Choice[int]]:
        events = await self.bot.db.events.get_all_of_user(i.user.id)
        if current:
            return [
                app_commands.Choice(
                    name=event.name,
                    value=event.id,
                )
                for event in events
                if current.lower() in event.name.lower()
            ][:25]
        else:
            return [
                app_commands.Choice(
                    name=event.name,
                    value=event.id,
                )
                for event in events
            ][:25]


async def setup(bot: Bot) -> None:
    """
    This function sets up the Schedule cog.

    Args:
        bot (Bot): The bot instance.

    Returns:
        None
    """
    await bot.add_cog(Schedule(bot))
