import asyncio
from contextlib import asynccontextmanager, contextmanager

import numpy as np

from prisma import Prisma


class Server:
    def __init__(self):
        self.db = Prisma()
        self.initialized = False
        self.connection: Prisma | None = None
        self.db_lock = asyncio.Lock()

    async def initialize(self):
        async with self.db_lock:
            if not self.initialized:
                await self.db.connect()
                self.initialized = True
                self.connection = self.db

    @asynccontextmanager
    async def get_connection(self):
        assert self.connection
        yield self.connection

    async def find_fist_by_embedding(self, embedding: np.ndarray):
        async with self.get_connection() as db:
            result = await db.product.query_raw(
                "SELECT * FROM Product WHERE embedding <=> $1 LIMIT 1", embedding
            )
            return result

    async def seed_db(self):
        async with self.get_connection() as db:
            result = await db.product.create_many()
