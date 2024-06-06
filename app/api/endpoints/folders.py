# api/endpoints/folders.py
import uuid
from typing import Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException
from app.auth import get_current_user
from app.crud.file import get_folder
from app.database import get_db
from app.models import Folder, FuFile
from app.schemas import User as UserSchema, FolderCreate
from app.utils import create_folder
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/create-folder/{folder_path:path}")
async def create_new_folder(
        folder_path: str, user: UserSchema = Depends(get_current_user)
):
    folder_path = folder_path.strip('/')
    create_folder(folder_path)
    return {"folder_path": folder_path}


# 查询文件夹列表及其关联的文件
@router.get("/folders")
def get_folders_tree(db: Session = Depends(get_db)):
    # Step 1: Retrieve folders from the database
    folders: List[Folder] = db.query(Folder).all()

    # Step 2: Create a dictionary to store folders by their ID
    folder_dict = {folder.id: folder for folder in folders}

    # Step 3: Initialize the 'sub_folders' attribute for each folder
    for folder in folders:
        folder.sub_folders = []

    # Step 4: Loop through the folders to nest them under their parent based on parent_id
    for folder in folders:
        if folder.parent_id:
            parent_folder = folder_dict[folder.parent_id]
            parent_folder.sub_folders.append(folder)

    # Step 5: Identify the root folders (where parent_id is None)
    root_folders = [folder for folder in folders if folder.parent_id is None]

    # Step 6: Convert the Folder objects to dictionaries for easier JSON serialization
    def folder_to_dict(folder: Folder) -> Dict[str, Any]:
        return {
            "id": folder.id,
            "name": folder.name,
            "parent_id": folder.parent_id,
            "sub_folders": [folder_to_dict(child) for child in folder.sub_folders]
        }

    # Convert all root folders to dictionary format
    root_folders_dicts = [folder_to_dict(folder) for folder in root_folders]

    return root_folders_dicts

# 根据文件夹 ID 查询当前文件夹下的子文件夹和文件
@router.get("/folders/{folder_id}")
def get_folder_contents(folder_id: str, db: Session = Depends(get_db)):
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        return {"error": "Folder not found"}

    sub_folders = db.query(Folder).filter(Folder.parent_id == folder_id).all()
    files = db.query(FuFile).filter(FuFile.folder_id == folder_id).all()

    folder_data = {
        "id": folder.id,
        "name": folder.name,
        "parent_id": folder.parent_id,
        "sub_folders": [{"id": sub.id, "name": sub.name} for sub in sub_folders],
        "files": [{"id": file.id, "name": file.name, "path": file.path} for file in files]
    }

    return folder_data
