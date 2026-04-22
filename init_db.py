import asyncio
import os
from dotenv import load_dotenv
import asyncpg
from backend.database.models import CREATE_TABLES_SQL

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:giri@localhost:5432/contractiq")

async def init_db():
    print(f"Connecting to database at {DATABASE_URL}...")
    try:
        # Connect to the database
        conn = await asyncpg.connect(DATABASE_URL) 
        print("✅ Connected to database")
        
        # Execute the schema creation script
        print("Creating tables...")
        await conn.execute(CREATE_TABLES_SQL)
        print("✅ Tables created successfully")
        
        await conn.close()
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        # Note: If the database "contractiq" doesn't exist, we might need to connect to "postgres"
        # and create the database first. The user instructions assumed `createdb contractiq` is run.

if __name__ == "__main__":
    asyncio.run(init_db())
