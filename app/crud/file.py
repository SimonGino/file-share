from sqlalchemy.orm import Session
from app.models import Folder, FuFile
from app.schemas import FolderCreate, FileCreate
import uuid
def create_folder(db: Session, folder: FolderCreate):
    db_folder = Folder(id=uuid.uuid4(), name=folder.name, parent_id=folder.parent_id)
    db.add(db_folder)
    db.commit()
    db.refresh(db_folder)
    return db_folder

def get_folder(db: Session, folder_id: uuid.UUID):
    return db.query(Folder).filter(Folder.id == folder_id).first()
def get_folder_by_name(db: Session, folder_name: str):
    return db.query(Folder).filter(Folder.name == folder_name).first()
def get_or_create_folder_by_path(db: Session, folder_path: str):
    folder_names = folder_path.split('/')  # 将路径按 '/' 分割成文件夹名称列表
    parent_folder = None
    current_folder = None

    for folder_name in folder_names:
        if parent_folder is None:
            current_folder = db.query(Folder).filter(Folder.name == folder_name, Folder.parent_id.is_(None)).first()
        else:
            current_folder = db.query(Folder).filter(Folder.name == folder_name, Folder.parent_id == parent_folder.id).first()

        if current_folder is None:
            # 如果当前文件夹不存在，则创建新文件夹
            new_folder = Folder(id=uuid.uuid4(), name=folder_name, parent_id=parent_folder.id if parent_folder else None)
            db.add(new_folder)
            db.commit()
            current_folder = new_folder

        parent_folder = current_folder

    return current_folder
def create_file(db: Session, file: FileCreate):
    db_file = FuFile(id=uuid.uuid4(), name=file.name, path=file.path, folder_id=file.folder_id)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def get_file(db: Session, file_id: uuid.UUID):
    return db.query(FuFile).filter(FuFile.id == file_id).first()