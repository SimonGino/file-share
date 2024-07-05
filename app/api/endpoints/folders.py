# api/endpoints/folders.py
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, Query
from app.auth import get_current_user
from app.storages.database import get_db
from app.models import Folder, FuFile
from app.schemas import User as UserSchema
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

# 根据文件夹 ID 查询当前文件夹下的子文件夹和文件
def get_folder_contents(folder_id: str, db: Session) -> Dict[str, Any]:
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        return {"error": "Folder not found"}

    sub_folders = db.query(Folder).filter(Folder.parent_id == folder_id).all()
    files = db.query(FuFile).filter(FuFile.folder_id == folder_id).all()

    children = [{"id": "...", "name": "..", "type": "folder", "children": []}]
    for sub in sub_folders:
        children.append({"id": sub.id, "name": sub.name, "type": "folder"})
    for file in files:
        children.append({"id": file.id, "name": file.name, "path": file.path, "type": "file"})

    folder_data = {
        "id": folder.id,
        "name": folder.name,
        "parent_id": folder.parent_id,
        "children": children
    }

    return folder_data

# 查询文件夹列表及其关联的文件
@router.get("/folders")
def get_folders_tree(folder_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    if folder_id:
        return get_folder_contents(folder_id, db)

    # Step 1: Retrieve folders from the database
    folders: List[Folder] = db.query(Folder).all()

    # Step 2: Create a dictionary to store folders by their ID
    folder_dict = {folder.id: folder for folder in folders}

    # Step 3: Initialize the 'children' attribute for each folder
    for folder in folders:
        folder.children = []

    # Step 4: Loop through the folders to nest them under their parent based on parent_id
    for folder in folders:
        if folder.parent_id:
            parent_folder = folder_dict[folder.parent_id]
            parent_folder.children.append(folder)

    # Step 5: Add files to their respective folders
    files: List[FuFile] = db.query(FuFile).all()
    for file in files:
        if file.folder_id in folder_dict:
            folder_dict[file.folder_id].children.append({"id": file.id, "name": file.name, "path": file.path, "type": "file"})

    # Step 6: Identify the root folders (where parent_id is None)
    root_folders = [folder for folder in folders if folder.parent_id is None]

    # Step 7: Convert the Folder objects to dictionaries for easier JSON serialization
    def folder_to_dict(folder: Folder) -> Dict[str, Any]:
        return {
            "id": folder.id,
            "name": folder.name,
            "parent_id": folder.parent_id,
            "children": [
                folder_to_dict(child) if isinstance(child, Folder) else child
                for child in folder.children
            ]
        }

    # Convert all root folders to dictionary format
    root_folders_dicts = [folder_to_dict(folder) for folder in root_folders]

    return root_folders_dicts