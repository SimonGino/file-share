from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Query
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from auth import authenticate_user, create_access_token, get_current_user
from schemas import UserCreate, User as UserSchema
from crud import create_user, get_user, get_user_by_username
from utils import save_file, get_file_path, create_folder
from redis_client import r
import os
import uuid
from database import SessionLocal
from database import engine
from models import Base

# 创建所有数据库表
Base.metadata.create_all(bind=engine)


app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register/", response_model=UserSchema)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(db=db, user=user)

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# 文件上传接口
@app.post("/upload/{folder_path:path}")
async def upload_file(
    folder_path: str, file: UploadFile = File(...), user: UserSchema = Depends(get_current_user)
):
    folder_path = folder_path.strip('/')
    file_path = save_file(file, folder_path)
    return {"filename": file.filename, "path": file_path}


# 未登录用户下载文件接口
@app.get("/api/download/{folder_path:path}/{file_name}")
async def download_file(
    folder_path: str, file_name: str, token: str = Query(...)
):
    # 验证token
    user_info = r.get(token)
    if not user_info:
        raise HTTPException(status_code=403, detail="Token expired or invalid")
    folder_path = folder_path.strip('/')
    file_path = get_file_path(folder_path, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


# 已登录用户下载文件接口
@app.get("/download/{folder_path:path}/{file_name}")
async def download_file_for_logged_in_user(
    folder_path: str, file_name: str, user: UserSchema = Depends(get_current_user)
):
    # 如果用户已经登录，则不需要提供 token，并且会自动校验用户信息
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    # 继续文件下载操作
    folder_path = folder_path.strip('/')
    file_path = get_file_path(folder_path, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

# 文件夹创建接口
@app.post("/create-folder/{folder_path:path}")
async def create_new_folder(
    folder_path: str, user: UserSchema = Depends(get_current_user)
):
    folder_path = folder_path.strip('/')
    create_folder(folder_path)
    return {"folder_path": folder_path}

# 文件分享接口
@app.post("/share/{folder_path:path}/{file_name}")
async def share_file(
    folder_path: str, file_name: str, user: UserSchema = Depends(get_current_user)
):
    folder_path = folder_path.strip('/')
    file_path = get_file_path(folder_path, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # 生成唯一的分享token
    share_token = str(uuid.uuid4())
    r.setex(share_token, 3600, user.username)  # token 有效期为 1 小时
    return {"share_url": f"/download/{folder_path}/{file_name}?token={share_token}"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
