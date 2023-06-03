from typing import Optional

import discord
import parsedatetime
from discord import app_commands
from discord.app_commands import locale_str as _T
from discord.ext import commands

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
        datetime=_T("datetime", context="commands.add.params.datetime.name"),
        recur=_T("recur", context="commands.add.params.recur.name"),
        recur_interval=_T(
            "recur_interval", context="commands.add.params.recur_interval.name"
        ),
    )
    @app_commands.describe(
        name=_T("name", context="commands.add.params.name.description"),
        datetime=_T("datetime", context="commands.add.params.datetime.description"),
        recur=_T("recur", context="commands.add.params.recur.description"),
        recur_interval=_T(
            "recur_interval", context="commands.add.params.recur_interval.description"
        ),
    )
    @app_commands.choices(
        recur=[
            app_commands.Choice(
                name=_T("Yes", context="commands.add.params.recur.choices.yes"), value=1
            ),
            app_commands.Choice(
                name=_T("No", context="commands.add.params.recur.choices.no"), value=0
            ),
        ],
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
        datetime: str,
        recur: int = 0,
        recur_interval: Optional[int] = None,
    ) -> None:
        converted_interval = RecurInterval(recur_interval) if recur_interval else None
        cal = parsedatetime.Calendar()
        datetime_obj, _ = cal.parseDT(datetimeString=datetime)
        event = Event(
            user_id=i.user.id,
            name=name,
            date_time=datetime_obj,
            recur=bool(recur),
            recur_interval=converted_interval,
        )
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
            name=translator.translate(lang, "commands.add.embed.fields.date_time.name"),
            value=f"{discord.utils.format_dt(event.date_time)}/{discord.utils.format_dt(event.date_time, 'R')}",
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
                value=f"- {discord.utils.format_dt(event.date_time)} ({discord.utils.format_dt(event.date_time, 'R')})\n- ID: {event.id}",
                inline=False,
            )
        embed.set_author(name=i.user.display_name, icon_url=i.user.display_avatar.url)
        embed.set_footer(
            text=translator.translate(lang, "commands.list.embed.footer").format(
                total=len(events)
            )
        )
        await i.response.send_message(embed=embed)


async def setup(bot: Bot) -> None:
    """
    This function sets up the Schedule cog.

    Args:
        bot (Bot): The bot instance.

    Returns:
        None
    """
    await bot.add_cog(Schedule(bot))
