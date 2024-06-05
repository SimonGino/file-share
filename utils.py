from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

import os
from fastapi import UploadFile

UPLOAD_DIRECTORY = "./uploaded_files"

def save_file(file: UploadFile, folder_path: str):
    full_folder_path = os.path.join(UPLOAD_DIRECTORY, folder_path)
    if not os.path.exists(full_folder_path):
        os.makedirs(full_folder_path)
    file_path = os.path.join(full_folder_path, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return file_path

def get_file_path(folder_path: str, file_name: str):
    return os.path.join(UPLOAD_DIRECTORY, folder_path, file_name)

def create_folder(folder_path: str):
    full_folder_path = os.path.join(UPLOAD_DIRECTORY, folder_path)
    if not os.path.exists(full_folder_path):
        os.makedirs(full_folder_path)
