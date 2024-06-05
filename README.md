# 文件服务器

本项目作为学习FastApi框架学习项目。



## requirements.txt

```sh
pip install pipreqs
```

```shell
pipreqs . --force
```

## Docker镜像打包和运行

```sh
docker build -t file-server .
```

```sh
docker run -d -p 8000:8000 -v /path/to/.env:/code/app/.env --name file-server-container file-server
```

## .env环境

| Key        | Value     | description  |
| ---------- | --------- | ------------ |
| redis_host | localhost | 主机         |
| redis_port | 6379      | 端口         |
| redis_db   | 0         | 数据库的编号 |

