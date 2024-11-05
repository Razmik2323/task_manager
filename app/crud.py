from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app import auth
from app.models import User, Task
from app.schemas import TaskCreate, Task
from app.database import get_db

router = APIRouter()

# Создание новой задачи
@router.post("/tasks", response_model=Task)
async def create_task(task_create: TaskCreate, db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(auth.get_current_user)):
    task = Task(**task_create.dict(), user_id=current_user.id)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

# Получение всех задач текущего пользователя (с возможностью фильтрации по статусу)
@router.get("/tasks", response_model=list[Task])
async def get_tasks(status: str = None, db: AsyncSession = Depends(get_db),
                    current_user: User = Depends(auth.get_current_user)):
    query = select(Task).filter(Task.user_id == current_user.id)

    if status:
        query = query.filter(Task.status == status)

    result = await db.execute(query)
    return result.scalars().all()

# Обновление существующей задачи по ID
@router.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task_update: TaskCreate, db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(auth.get_current_user)):
    task = await db.get(Task, task_id)

    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    for key, value in task_update.dict().items():
        setattr(task, key, value)

    await db.commit()
    await db.refresh(task)

    return task

# Удаление задачи по ID
@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(auth.get_current_user)):
    task = await db.get(Task, task_id)

    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.delete(task)
    await db.commit()

    return {"detail": "Task deleted"}
