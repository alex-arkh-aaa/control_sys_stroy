from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import *


async def create_user(db: AsyncSession, name: str, email: str, age: int, hashed_password: str, job_title: str):
    user = User(name=name, email=email, age=age, hashed_password=hashed_password, job_title=job_title)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, user_email: str):
    result = await db.execute(select(User).where(User.email == user_email))
    return result.scalar_one_or_none()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()

async def delete_user(db: AsyncSession, user_id: int):
    user = await get_user(db, user_id)
    if user:
        await db.delete(user)
        await db.commit()
    return user




async def create_project(db: AsyncSession, name: str, address: str, description: str, created_by: int):
    project = Project(name=name, address=address, description=description, created_by=created_by)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project

async def get_project(db: AsyncSession, project_id: int):
    result = await db.execute(select(Project).where(Project.id == project_id))
    return result.scalar_one_or_none()

async def get_projects(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Project).offset(skip).limit(limit))
    return result.scalars().all()

async def create_defect(db: AsyncSession, title: str, description: str, project_id: int, author_id: int,
                       priority: str = "medium", assignee_id: int = None, due_date = None):
    defect = Defect(
        title=title, description=description, project_id=project_id, author_id=author_id,
        priority=priority, assignee_id=assignee_id, due_date=due_date
    )
    db.add(defect)
    await db.commit()
    await db.refresh(defect)
    return defect

async def get_defect(db: AsyncSession, defect_id: int):
    result = await db.execute(select(Defect).where(Defect.id == defect_id))
    return result.scalar_one_or_none()

async def get_defects_by_project(db: AsyncSession, project_id: int, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(Defect).where(Defect.project_id == project_id).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def update_defect(db: AsyncSession, defect_id: int, **kwargs):
    defect = await get_defect(db, defect_id)
    if defect:
        for key, value in kwargs.items():
            if value is not None:
                setattr(defect, key, value)
        await db.commit()
        await db.refresh(defect)
    return defect

async def create_comment(db: AsyncSession, text: str, defect_id: int, author_id: str):
    comment = Comment(text=text, defect_id=defect_id, author_id=author_id)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment

async def get_comments_by_defect(db: AsyncSession, defect_id: int, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(Comment).where(Comment.defect_id == defect_id).offset(skip).limit(limit)
    )
    return result.scalars().all()




async def update_project(db: AsyncSession, project_id: int, **kwargs):
    project = await get_project(db, project_id)
    if project:
        for key, value in kwargs.items():
            if value is not None:
                setattr(project, key, value)
        await db.commit()
        await db.refresh(project)
    return project