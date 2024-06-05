# 使用官方的 Python 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /code

# 复制项目的依赖文件
#COPY requirements.txt .
COPY ./requirements.txt /code/requirements.txt
# 安装项目依赖
#RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 复制项目文件
COPY ./app /code/app

# 暴露应用运行的端口
EXPOSE 8000

# 运行应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]