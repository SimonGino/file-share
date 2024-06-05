# app/utils/folders.py
import os

UPLOAD_DIRECTORY = "./uploaded_files"

def create_folder(folder_path: str):
    full_folder_path = os.path.join(UPLOAD_DIRECTORY, folder_path)
    if not os.path.exists(full_folder_path):
        os.makedirs(full_folder_path)