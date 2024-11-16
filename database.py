from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from cat_spy_agency_app.models import Base
from settings import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
