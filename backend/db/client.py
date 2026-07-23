from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from dotenv import load_dotenv
import os
load_dotenv()

engine = create_async_engine(os.getenv("DATABASE_URL"))
AsyncSessionLocal = async_sessionmaker(bind=engine)


async def get_db():
    async with AsyncSessionLocal() as db:
        yield db