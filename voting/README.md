# Flask Redisのサンプル

## 動作環境

- python3.9
- flask3.1.0

## 環境構築

### 仮想環境(poetry)

poetryのインストール(インストール済みの場合は不要)

```zsh
  curl -sSL https://install.python-poetry.org | python3 -
```

ライブラリのインストール

```zsh
poetry install  
```

### docker

#### mysql

```zsh
docker run --name mysql_for_redis -e MYSQL_ROOT_PASSWORD=my-secret-pw -p 3306:3306 -d mysql

docker exec -it [コンテナID] bash

mysql -u root -pmy-secret-pw
CREATE USER app@'%' IDENTIFIED BY 'P@ssw0rd';
GRANT ALL PRIVILEGES on voting.* to app@'%';
CREATE DATABASE voting DEFAULT CHARACTER SET utf8mb4;
USE voting
CREATE TABLE votes (
     id INT NOT NULL AUTO_INCREMENT,
     candidate VARCHAR(128) NOT NULL,
     voter VARCHAR(140),
     PRIMARY KEY (id)
);
```

#### redis

```zsh
docker run -it --name redis_server -p 6379:6379 --rm redis
```

## Server起動

```zsh
 hypercorn main:app
```
