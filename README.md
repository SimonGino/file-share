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
docker-compose up --build

```

```sh
docker-compose up --d
```

## .env环境

| Key        | Value     | description  |
| ---------- | --------- | ------------ |
| redis_host | localhost | 主机         |
| redis_port | 6379      | 端口         |
| redis_db   | 0         | 数据库的编号 |

