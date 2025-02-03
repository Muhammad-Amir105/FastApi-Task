import secrets
from app.schema import UserCreate,TaskCreate, TaskResponse
from fastapi import APIRouter, Depends, HTTPException, Request
from app.database import AsyncSessionLocal
from app.model import Task, User
from typing import List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.model import Token

router = APIRouter()




async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/createuser/", status_code=201)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.username == user.username))
    db_user = result.scalars().first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    db_user = User(**user.dict())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_current_token(request: Request) -> Token:
    token_entry: Token = getattr(request.state, "token_entry", None)
    if not token_entry:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return token_entry

@router.post("/createtask/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    db: AsyncSession = Depends(get_db),
    token_entry: Token = Depends(get_current_token),
):

    db_task = Task(
        name=task.name,
        description=task.description,
        user_id=token_entry.user_id,
    )
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

@router.get("/tasks/", response_model=List[TaskResponse])
async def get_tasks_for_user(
    db: AsyncSession = Depends(get_db),
    token_entry: Token = Depends(get_current_token),
):

    result = await db.execute(select(Task).filter(Task.user_id == token_entry.user_id))
    tasks = result.scalars().all()

    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found for the user")

    return tasks



@router.post("/login/", status_code=200)
async def login(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.username == user.username))
    db_user = result.scalars().first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if db_user.password != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    result = await db.execute(select(Token).filter(Token.user_id == db_user.id))
    existing_token = result.scalars().first()

    if existing_token:
        token_age = datetime.utcnow() - existing_token.created_at
        if token_age < timedelta(hours=10):
            return {"message": "Login successful", "token": existing_token.token}

        existing_token.token = secrets.token_hex(32)
        existing_token.created_at = datetime.utcnow()
        await db.commit()
        return {"message": "Login successful (new token issued)", "token": existing_token.token}

    new_token = Token(
        token=secrets.token_hex(32),
        user_id=db_user.id,
        created_at=datetime.utcnow()
    )
    db.add(new_token)
    await db.commit()
    return {"message": "Login successful (new token issued)", "token": new_token.token}

