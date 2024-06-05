# api/endpoints/files.py
import uuid

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query
from fastapi.responses import FileResponse
from app.auth import get_current_user
from app.schemas import User as UserSchema
from app.utils.file import save_file, get_file_path
from app.redis_client import r
import os

router = APIRouter()

@router.post("/upload/{folder_path:path}")
async def upload_file(
    folder_path: str, file: UploadFile = File(...), user: UserSchema = Depends(get_current_user)
):
    folder_path = folder_path.strip('/')
    file_path = save_file(file, folder_path)
    return {"filename": file.filename, "path": file_path}

@router.get("/download/{folder_path:path}/{file_name}")
async def download_file_for_logged_in_user(
    folder_path: str, file_name: str, user: UserSchema = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    folder_path = folder_path.strip('/')
    file_path = get_file_path(folder_path, file_name)
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