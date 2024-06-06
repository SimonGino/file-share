# api/endpoints/files.py
import uuid

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.auth import get_current_user
from app.crud.file import create_file, get_file, create_folder, get_folder_by_name, get_or_create_folder_by_path
from app.database import get_db
from app.schemas import User as UserSchema, FileCreate, FolderCreate
from app.utils.file import save_file, get_file_path
from app.redis_client import r
import os

router = APIRouter()

@router.post("/upload")
async def upload_file(
    folder_path: str, file: UploadFile = File(...), db: Session = Depends(get_db), user: UserSchema = Depends(get_current_user)
):
    result = None
    # 检查是否存在重复的文件夹名称
    existing_folder = get_or_create_folder_by_path(db, folder_path)

    if not existing_folder:
        # 处理文件夹处理失败的情况，可以创建默认文件夹或返回错误信息
        return {"error": "Failed to create folder"}

    # 确保成功创建文件夹后再创建文件数据
    file_data = FileCreate(name=file.filename, path=folder_path, folder_id=existing_folder.id)
    result = create_file(db, file_data)
    file_path = save_file(file)

    return {"filename": file.filename, "path": file_path, "file_id": result.id}

@router.get("/download/{file_name}")
async def download_file_for_logged_in_user(
    file_name: str, user: UserSchema = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    file_path = get_file_path( file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@router.get("/api/download/{folder_path:path}/{file_name}")
async def download_file(
    folder_path: str, file_name: str, token: str = Query(...)
):
    user_info = r.get(token)
    if not user_info:
        raise HTTPException(status_code=403, detail="Token expired or invalid")
    folder_path = folder_path.strip('/')
    file_path = get_file_path(folder_path, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@router.post("/share/{folder_path:path}/{file_name}")
async def share_file(
    folder_path: str, file_name: str, user: UserSchema = Depends(get_current_user)
):
    folder_path = folder_path.strip('/')
    file_path = get_file_path(folder_path, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    share_token = str(uuid.uuid4())
    r.setex(share_token, 3600, user.username)
    return {"share_url": f"/files/api/download/{folder_path}/{file_name}?token={share_token}"}

#
# @router.post("/files/")
# def create_new_file(file: FileCreate, db: Session = Depends(get_db)):
#     return create_file(db=db, file=file)
#
# @router.get("/files/{file_id}")
# def read_file(file_id: uuid.UUID, db: Session = Depends(get_db)):
#     db_file = get_file(db, file_id=file_id)
#     if db_file is None:
#         raise HTTPException(status_code=404, detail="File not found")
#     return db_file