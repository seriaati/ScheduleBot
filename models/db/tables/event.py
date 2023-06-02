from datetime import datetime
from typing import Optional

import aiosqlite
from pydantic import BaseModel, Field


class Event(BaseModel):
    """
    This class represents an event in the database.

    Attributes:
        id (int): The id of the event.
        user_id (int): The id of the user that created the event.
        name (str): The name of the event.
        datetime (datetime): The date and time of the event.
        recur (bool): Whether the event is recurring or not.
        recur_interval (Optional[int]): The interval of recurrence. This is only set if the event is recurring.
    """

    id: int
    user_id: int
    name: str
    datetime: datetime
    recur: bool
    recur_interval: Optional[int] = Field(None, gt=0)


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
                recur_interval INTEGER NOT NULL
            )
            """
        )
        await self.conn.commit()
