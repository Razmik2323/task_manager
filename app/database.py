from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app import models

DATABASE_URL = "postgresql+asyncpg://user:password@db/task_manager"

engine = create_async_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# Инициализация базы данных (создание таблиц)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

# Закрытие соединения с базой данных
async def close_db():
    await engine.dispose()

# Генерация зависимости для доступа к базе данных
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
