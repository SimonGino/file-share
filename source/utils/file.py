# source/utils/files.py
import os
from fastapi import UploadFile
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

UPLOAD_DIRECTORY = "./uploaded_files"

def save_file(file: UploadFile):
    full_folder_path = os.path.join(UPLOAD_DIRECTORY)
    if not os.path.exists(full_folder_path):
        os.makedirs(full_folder_path)
    file_path = os.path.join(full_folder_path, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return file_path

def get_file_path( file_name: str):
    return os.path.join(UPLOAD_DIRECTORY, file_name)