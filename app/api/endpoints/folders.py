# api/endpoints/folders.py
from fastapi import APIRouter, Depends, HTTPException
from app.auth import get_current_user
from app.schemas import User as UserSchema
from app.utils import create_folder

router = APIRouter()

@router.post("/create-folder/{folder_path:path}")
async def create_new_folder(
    folder_path: str, user: UserSchema = Depends(get_current_user)
):
    folder_path = folder_path.strip('/')
    create_folder(folder_path)
    return {"folder_path": folder_path}