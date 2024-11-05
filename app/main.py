from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app import crud, auth, database

app = FastAPI()

# Инициализация базы данных
DATABASE_URL = "postgresql+asyncpg://user:password@db/task_manager"
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

@app.on_event("startup")
async def startup():
    await database.init_db()

@app.on_event("shutdown")
async def shutdown():
    await database.close_db()

# Маршруты аутентификации и задач
app.include_router(auth.router)
app.include_router(crud.router)

