from fastapi import FastAPI, Header, responses, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_db, create_tables
from . import crud
from .schemas import *
from contextlib import asynccontextmanager
from .security import *
from .send_notifies import *
from sqlalchemy import select

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import HTMLResponse



@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    print("✅ Таблицы созданы/проверены")
    yield



app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

async def get_current_user(authorization: str = Header(...), db: AsyncSession = Depends(get_db)):
    # 1. Проверяем формат заголовка Authorization
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    
    # 2. Извлекаем чистый токен из "Bearer <token>"
    token = authorization.replace("Bearer ", "")
    
    # 3. Декодируем и проверяем токен (включая черный список)
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # 4. Извлекаем email из payload (в токене хранится {"sub": "user@email.com"})
    user_email = payload.get("sub")
    if not user_email:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    # 5. Ищем пользователя в БД по email
    user = await crud.get_user_by_email(db, user_email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # 6. Возвращаем объект пользователя
    return user

# ==================== АУТЕНТИФИКАЦИЯ ====================
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
    
    await crud.delete_user(db, existing_user.id)
    
    return {"message": "User deleted"}

# @app.get("/register/", response_class=HTMLResponse)
# async def show_registration_form(request: Request):
#     return templates.TemplateResponse("registration.html", {"request": request})

@app.post("/register/")
async def register_user(user: User, db: AsyncSession = Depends(get_db)):
    existing_user = await crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    hashed_password = get_password_hash(user.password)
    new_user = await crud.create_user(db, user.name, user.email, user.age, hashed_password, user.job_title)

    message = 'Поздравляем Вас с началом работы в Control System!'
    data = {"email": new_user.email, "message": message, "full_name": new_user.name,  "subject": 'Успешная регистрация!'}
    ans = await send_notification(data)
    print(ans)

    return {"msg": "Пользователь успешно зарегистрирован", 'user': new_user}

# @app.get("/login/", response_class=HTMLResponse)
# async def show_login_form(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})


@app.post("/token")
async def login(user_creds: UserCreds, db: AsyncSession = Depends(get_db)):
    '''
    Вход в аккаунт (авторизация)
    '''
    existing_user = await crud.get_user_by_email(db, user_creds.email)

    if not existing_user or not verify_password(user_creds.password, existing_user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    token_data = {"sub": user_creds.email}
    access_token = create_access_token(data=token_data)
    print(existing_user.email, existing_user.hashed_password)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/logout")
async def logout(authorization: str = Header(...), current_user: User = Depends(get_current_user)):
    """
    Выход из системы - добавление токена в черный список
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    
    token = authorization.replace("Bearer ", "")
    
    # Добавляем токен в черный список
    revoke_token(token)
    
    return {"message": "Successfully logged out"}


# # ==================== ПРОЕКТЫ ====================
# @app.get("/", response_class=HTMLResponse)
# async def projects_page(request: Request):
#     return templates.TemplateResponse("projects.html", {"request": request})




# @app.get("/api/projects/", response_model=list[ProjectResponse])
# async def read_projects(
#     skip: int = 0, 
#     limit: int = 100, 
#     db: AsyncSession = Depends(get_db),
#     authorization: str = Header(...)
# ):
#     current_user = await get_current_user(authorization, db)
#     return await crud.get_projects(db, skip=skip, limit=limit)

# @app.post("/api/projects/", response_model=ProjectResponse)
# async def create_project_api(
#     project: ProjectCreate,
#     db: AsyncSession = Depends(get_db),
#     authorization: str = Header(...)
# ):
#     current_user = await get_current_user(authorization, db)
#     check_create_project_permission(current_user)
#     return await crud.create_project(
#         db, 
#         name=project.name,
#         address=project.address,
#         description=project.description,
#         created_by=current_user.id
#     )

# @app.get("/api/projects/{project_id}", response_model=ProjectResponse)
# async def read_project(
#     project_id: int,
#     db: AsyncSession = Depends(get_db),
#     authorization: str = Header(...)
# ):
#     current_user = await get_current_user(authorization, db)
#     await check_project_access(db, project_id, current_user)
#     project = await crud.get_project(db, project_id)
#     if not project:
#         raise HTTPException(status_code=404, detail="Project not found")
#     return project

# # ==================== ДЕФЕКТЫ ====================
# @app.get("/projects/{project_id}/defects-page/", response_class=HTMLResponse)
# async def defects_page(request: Request, project_id: int):
#     return templates.TemplateResponse("defects.html", {"request": request})


# @app.get("/api/projects/{project_id}/defects/", response_model=list[DefectResponse])
# async def read_defects_api(
#     project_id: int,
#     skip: int = 0,
#     limit: int = 100,
#     db: AsyncSession = Depends(get_db),
#     authorization: str = Header(...)
# ):
#     current_user = await get_current_user(authorization, db)
#     await check_project_access(db, project_id, current_user)
#     return await crud.get_defects_by_project(db, project_id, skip=skip, limit=limit)

# @app.post("/projects/{project_id}/defects/", response_model=DefectResponse)
# async def create_defect(
#     project_id: int,
#     defect: DefectCreate,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     await check_project_access(db, project_id, current_user)
#     return await crud.create_defect(
#         db,
#         title=defect.title,
#         description=defect.description,
#         project_id=project_id,
#         author_id=current_user.id,
#         priority=defect.priority,
#         assignee_id=defect.assignee_id,
#         due_date=defect.due_date
#     )

# @app.get("/projects/{project_id}/defects/{defect_id}", response_model=DefectResponse)
# async def read_defect(
#     project_id: int,
#     defect_id: int,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     await check_project_access(db, project_id, current_user)
#     defect = await crud.get_defect(db, defect_id)
#     if not defect or defect.project_id != project_id:
#         raise HTTPException(status_code=404, detail="Defect not found")
#     return defect

# @app.put("/projects/{project_id}/defects/{defect_id}", response_model=DefectResponse)
# async def update_defect(
#     project_id: int,
#     defect_id: int,
#     defect_update: DefectUpdate,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     await check_project_access(db, project_id, current_user)
#     defect = await crud.get_defect(db, defect_id)
#     if not defect or defect.project_id != project_id:
#         raise HTTPException(status_code=404, detail="Defect not found")
    
#     check_edit_defect_permission(current_user, defect)
    
#     update_data = defect_update.dict(exclude_unset=True)
#     return await crud.update_defect(db, defect_id, **update_data)

# # ==================== КОММЕНТАРИИ ====================

# @app.post("/projects/{project_id}/defects/{defect_id}/comments/", response_model=CommentResponse)
# async def create_comment(
#     project_id: int,
#     defect_id: int,
#     comment: CommentCreate,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     await check_project_access(db, project_id, current_user)
#     defect = await crud.get_defect(db, defect_id)
#     if not defect or defect.project_id != project_id:
#         raise HTTPException(status_code=404, detail="Defect not found")
    
#     return await crud.create_comment(
#         db,
#         text=comment.text,
#         defect_id=defect_id,
#         author_id=current_user.id
#     )

# @app.get("/projects/{project_id}/defects/{defect_id}/comments/", response_model=list[CommentResponse])
# async def read_comments(
#     project_id: int,
#     defect_id: int,
#     skip: int = 0,
#     limit: int = 100,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     await check_project_access(db, project_id, current_user)
#     defect = await crud.get_defect(db, defect_id)
#     if not defect or defect.project_id != project_id:
#         raise HTTPException(status_code=404, detail="Defect not found")
    
#     return await crud.get_comments_by_defect(db, defect_id, skip=skip, limit=limit)

# ==================== API ЭНДПОИНТЫ ====================

# Projects API
@app.get("/api/projects/", response_model=list[ProjectResponse])
async def read_projects_api(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    authorization: str = Header(...)
):
    current_user = await get_current_user(authorization, db)
    return await crud.get_projects(db, skip=skip, limit=limit)

@app.post("/api/projects/", response_model=ProjectResponse)
async def create_project_api(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    authorization: str = Header(...)
):
    current_user = await get_current_user(authorization, db)
    check_create_project_permission(current_user)
    return await crud.create_project(
        db, 
        name=project.name,
        address=project.address,
        description=project.description,
        created_by=current_user.id
    )

@app.get("/api/projects/{project_id}", response_model=ProjectResponse)
async def read_project_api(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    authorization: str = Header(...)
):
    current_user = await get_current_user(authorization, db)
    await check_project_access(db, project_id, current_user)
    project = await crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

# Defects API
@app.get("/api/projects/{project_id}/defects/", response_model=list[DefectResponse])
async def read_defects_api(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    authorization: str = Header(...)
):
    current_user = await get_current_user(authorization, db)
    await check_project_access(db, project_id, current_user)
    return await crud.get_defects_by_project(db, project_id, skip=skip, limit=limit)

@app.post("/api/projects/{project_id}/defects/", response_model=DefectResponse)
async def create_defect_api(
    project_id: int,
    defect: DefectCreate,
    db: AsyncSession = Depends(get_db),
    authorization: str = Header(...)
):
    current_user = await get_current_user(authorization, db)
    await check_project_access(db, project_id, current_user)
    return await crud.create_defect(
        db,
        title=defect.title,
        description=defect.description,
        project_id=project_id,
        author_id=current_user.id,
        priority=defect.priority,
        assignee_id=defect.assignee_id,
        due_date=defect.due_date
    )

@app.get("/api/projects/{project_id}/defects/{defect_id}", response_model=DefectResponse)
async def read_defect_api(
    project_id: int,
    defect_id: int,
    db: AsyncSession = Depends(get_db),
    authorization: str = Header(...)
):
    current_user = await get_current_user(authorization, db)
    await check_project_access(db, project_id, current_user)
    defect = await crud.get_defect(db, defect_id)
    if not defect or defect.project_id != project_id:
        raise HTTPException(status_code=404, detail="Defect not found")
    return defect

@app.put("/api/projects/{project_id}/defects/{defect_id}", response_model=DefectResponse)
async def update_defect_api(
    project_id: int,
    defect_id: int,
    defect_update: DefectUpdate,
    db: AsyncSession = Depends(get_db),
    authorization: str = Header(...)
):
    current_user = await get_current_user(authorization, db)
    await check_project_access(db, project_id, current_user)
    defect = await crud.get_defect(db, defect_id)
    if not defect or defect.project_id != project_id:
        raise HTTPException(status_code=404, detail="Defect not found")
    
    check_edit_defect_permission(current_user, defect)
    
    update_data = defect_update.dict(exclude_unset=True)
    return await crud.update_defect(db, defect_id, **update_data)

# Comments API
@app.post("/api/projects/{project_id}/defects/{defect_id}/comments/", response_model=CommentResponse)
async def create_comment_api(
    project_id: int,
    defect_id: int,
    comment: CommentCreate,
    db: AsyncSession = Depends(get_db),
    authorization: str = Header(...)
):
    current_user = await get_current_user(authorization, db)
    await check_project_access(db, project_id, current_user)
    defect = await crud.get_defect(db, defect_id)
    if not defect or defect.project_id != project_id:
        raise HTTPException(status_code=404, detail="Defect not found")
    
    return await crud.create_comment(
        db,
        text=comment.text,
        defect_id=defect_id,
        author_id=current_user.id
    )

@app.get("/api/projects/{project_id}/defects/{defect_id}/comments/", response_model=list[CommentResponse])
async def read_comments_api(
    project_id: int,
    defect_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    authorization: str = Header(...)
):
    current_user = await get_current_user(authorization, db)
    await check_project_access(db, project_id, current_user)
    defect = await crud.get_defect(db, defect_id)
    if not defect or defect.project_id != project_id:
        raise HTTPException(status_code=404, detail="Defect not found")
    
    return await crud.get_comments_by_defect(db, defect_id, skip=skip, limit=limit)

# Users API (тоже с префиксом для consistency)
@app.get("/api/users/", response_model=list[UserResponse])
async def read_users_api(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    authorization: str = Header(...)
):
    current_user = await get_current_user(authorization, db)
    print(current_user)
    ans = await crud.get_users(db, skip=skip, limit=limit)
    print(ans)
    return [current_user]   

# @app.get("/api/users/{user_id}", response_model=UserResponse)
# async def read_user_api(
#     user_id: int,
#     db: AsyncSession = Depends(get_db),
#     authorization: str = Header(...)
# ):
#     current_user = await get_current_user(authorization, db)
#     user = await crud.get_user(db, user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user

# ==================== HTML СТРАНИЦЫ ====================

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("projects.html", {"request": request})

@app.get("/projects/{project_id}/defects-page/", response_class=HTMLResponse)
async def defects_page(request: Request, project_id: int):
    return templates.TemplateResponse("defects.html", {"request": request})

@app.get("/register/", response_class=HTMLResponse)
async def show_registration_form(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})

@app.get("/login/", response_class=HTMLResponse)
async def show_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})










# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("app", host="127.0.0.1", port=8000, reload=True)

#uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
