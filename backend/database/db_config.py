# backend/database/db_config.py

import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:giri@localhost:5432/contractiq")

class Database:
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        """Create connection pool"""
        self.pool = await asyncpg.create_pool(DATABASE_URL, min_size=5, max_size=20)
        print("✅ Database connected")
        return self.pool
    
    async def disconnect(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            print("✅ Database disconnected")
    
    async def execute(self, query, *args):
        """Execute a query"""
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query, *args):
        """Fetch multiple rows"""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetch_one(self, query, *args):
        """Fetch one row"""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

# Create global database instance
db = Database()