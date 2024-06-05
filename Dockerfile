# 使用官方的 Python 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制项目的依赖文件
COPY requirements.txt .

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 设置 PYTHONPATH 环境变量
ENV PYTHONPATH=/app

# 暴露应用运行的端口
EXPOSE 8000

# 运行应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]