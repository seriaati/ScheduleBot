import aiosqlite


class DataBase:
    conn: aiosqlite.Connection
    
    async def start(self) -> None:
        await self.connect()
        await self.create_tables()
    
    async def connect(self):
        self.conn = await aiosqlite.connect("schedule_bot.db")
    
    async def create_tables(self):
        pass
    
    async def close(self):
        await self.conn.close()