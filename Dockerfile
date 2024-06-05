# 使用 Python 官方提供的基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 将项目文件复制到镜像中
COPY . .

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制配置文件到镜像中
COPY .env /app/.env

# 暴露端口
EXPOSE 8000

# 启动应用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

