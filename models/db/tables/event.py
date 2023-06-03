from datetime import datetime
from enum import Enum
from typing import List, Optional

import aiosqlite
from pydantic import BaseModel, validator
from pytz import timezone


class RecurInterval(Enum):
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3
    YEARLY = 4


class Event(BaseModel):
    """
    This class represents an event in the database.

    Attributes:
        id (int, optional): The id of the event.
        user_id (int): The id of the user who created the event.
        name (str): The name of the event.
        when (datetime): The date and time of the event.
        recur (bool): Whether or not the event recurs.
        recur_interval (RecurInterval, optional): The interval at which the event recurs.
    """

    id: int = None
    user_id: int
    name: str
    when: datetime
    recur: bool
    recur_interval: Optional[RecurInterval] = None

    @validator("when", pre=True)
    def convert_datetime(cls, v: str) -> datetime:
        """
        This validator converts the datetime string to a datetime object.

        Args:
            v (str): The datetime string.

        Returns:
            datetime: The datetime object.
        """
        if isinstance(v, datetime):
            return v
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=timezone("Asia/Taipei")
        )


class EventTable:
    """
    This class represents the events table.
    """

    def __init__(self, conn: aiosqlite.Connection) -> None:
        self.conn = conn

    async def create_table(self) -> None:
        """
        This method creates the events table if it does not exist.

        Returns:
            None
        """
        await self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                datetime TEXT NOT NULL,
                recur INTEGER NOT NULL,
                recur_interval INTEGER
            )
            """
        )
        await self.conn.commit()

    async def add(self, event: Event) -> None:
        """
        This method adds an event to the table.

        Args:
            event (Event): The event to add.

        Returns:
            None
        """
        await self.conn.execute(
            """
            INSERT INTO events (user_id, name, datetime, recur, recur_interval)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                event.user_id,
                event.name,
                event.when.strftime("%Y-%m-%d %H:%M:%S"),
                int(event.recur),
                event.recur_interval.value if event.recur_interval else None,
            ),
        )
        await self.conn.commit()

    async def get_all(self) -> List[Event]:
        """
        This method gets all the events in the table.

        Returns:
            List[Event]: The list of events.
        """
        cursor = await self.conn.execute(
            """
            SELECT id, user_id, name, datetime, recur, recur_interval
            FROM events
            """
        )
        rows = await cursor.fetchall()
        return [
            Event(
                id=row[0],
                user_id=row[1],
                name=row[2],
                when=row[3],
                recur=row[4],
                recur_interval=row[5],
            )
            for row in rows
        ]

    async def get_all_of_user(self, user_id: int) -> List[Event]:
        """
        This method gets all the events of the given user.

        Args:
            user_id (int): The id of the user.

        Returns:
            List[Event]: The list of events.
        """
        cursor = await self.conn.execute(
            """
            SELECT id, user_id, name, datetime, recur, recur_interval
            FROM events
            WHERE user_id = ?
            ORDER BY datetime ASC
            """,
            (user_id,),
        )
        rows = await cursor.fetchall()
        return [
            Event(
                id=row[0],
                user_id=row[1],
                name=row[2],
                when=row[3],
                recur=row[4],
                recur_interval=row[5],
            )
            for row in rows
        ]

    async def update(self, id: int, **kwargs) -> None:
        """
        This method updates the event with the given id.

        Args:
            id (int): The id of the event to update.
            **kwargs: The fields to update.

        Returns:
            None
        """
        query = "UPDATE events SET "
        for key, value in kwargs.items():
            query += f"{key} = {value}, "
        query = query[:-2]
        query += f" WHERE id = {id}"
        await self.conn.execute(query)
        await self.conn.commit()

    async def delete(self, id: int) -> None:
        """
        This method deletes the event with the given id.

        Args:
            id (int): The id of the event to delete.

        Returns:
            None
        """
        await self.conn.execute(
            """
            DELETE FROM events
            WHERE id = ?
            """,
            (id,),
        )
        await self.conn.commit()
