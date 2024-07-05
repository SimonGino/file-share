# source/main.py
from fastapi import FastAPI
from source.api.endpoints import auth, files, folders, minio
from source.storages.database import engine,Base
from fastapi.middleware.cors import CORSMiddleware

# 创建所有数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(files.router, prefix="/files", tags=["files"])
app.include_router(folders.router, prefix="/folders", tags=["folders"])
app.include_router(minio.router, prefix="/minio", tags=["minio"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)