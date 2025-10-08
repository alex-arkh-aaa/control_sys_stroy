import sys
import os
from pathlib import Path

# Добавляем корень проекта в Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, responses, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, create_tables
from app import crud
from app.schemas import *
from contextlib import asynccontextmanager
from app.security import *
from sqlalchemy import select

# Теперь импорты shared должны работать
from shared.rabbitmq import rabbit_manager
from app.events import user_publisher
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Подключаем RabbitMQ при старте
    await rabbit_manager.connect()
    print("✅ RabbitMQ connected")
    
    # Создаем таблицы БД
    await create_tables()
    print("✅ Таблицы созданы/проверены")
    yield

app = FastAPI(lifespan=lifespan)

# User endpoints
@app.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/", response_model=list[UserResponse])
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.get_users(db, skip=skip, limit=limit)

@app.delete("/users/")
async def delete_user(user_creds: UserCreds, db: AsyncSession = Depends(get_db)):
    existing_user = await crud.get_user_by_email(db, user_creds.email)

    if not existing_user or not verify_password(user_creds.password, existing_user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    
    # Сохраняем данные перед удалением для события
    user_email = existing_user.email
    user_name = existing_user.name
    user_id = existing_user.id
    
    await crud.delete_user(db, existing_user.id)
    
    # Отправляем событие в RabbitMQ
    await user_publisher.publish_user_deleted(user_id, user_email, user_name)
    
    return {"message": "User deleted"}

@app.post("/register/")
async def register_user(user: User, db: AsyncSession = Depends(get_db)):
    existing_user = await crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    hashed_password = get_password_hash(user.password)
    new_user = await crud.create_user(db, user.name, user.email, user.age, hashed_password)
    
    # Отправляем событие в RabbitMQ
    await user_publisher.publish_user_registered(new_user.id, user.email, user.name)
    
    return {"msg": "Пользователь успешно зарегистрирован", 'user': new_user}

@app.post("/token")
async def login(user_creds: UserCreds, db: AsyncSession = Depends(get_db)):
    existing_user = await crud.get_user_by_email(db, user_creds.email)

    if not existing_user or not verify_password(user_creds.password, existing_user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    token_data = {"sub": user_creds.email}
    access_token = create_access_token(data=token_data)
    return {"access_token": access_token, "token_type": "bearer"}