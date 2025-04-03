from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings
from .models import Base
import asyncio

SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@{settings.database_hostname}:{settings.database_port}/{settings.postgres_db}"
print('SQLALCHEMY_DATABASE_URL:', SQLALCHEMY_DATABASE_URL)
try:
    engine = create_async_engine(SQLALCHEMY_DATABASE_URL, future=True, echo=True)
    print("Database engine created successfully.")
except Exception as e:
    print(f"Error creating database engine: {e}")

SessionLocal = sessionmaker(bind=engine, autocommit=False, expire_on_commit=False, autoflush=False, class_=AsyncSession)

async def get_db():
    async with SessionLocal() as session:
        yield session

async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")\
        
# async def main():
#     await init_db()

# if __name__ == "__main__":
#     asyncio.run(main())
