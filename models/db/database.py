import aiosqlite

from .tables.event import EventTable


class DataBase:
    """
    This class represents the database.
    """

    conn: aiosqlite.Connection
    events: EventTable

    async def start(self) -> None:
        """
        This method starts the database.

        This method connects to the database and creates the tables.

        Returns:
            None
        """
        await self.connect()
        self.events = EventTable(self.conn)
        await self.create_tables()

    async def connect(self) -> None:
        """
        This method connects to the database.

        Returns:
            None
        """
        self.conn = await aiosqlite.connect("schedule_bot.db")

    async def create_tables(self) -> None:
        """
        This method creates the tables.

        Returns:
            None
        """
        await self.events.create_table()

    async def close(self) -> None:
        """
        This method closes the database connection.

        Returns:
            None
        """
        await self.conn.close()
