# Flask Redisのサンプル

## 動作環境

- python3.9
- flask3.1.0

## 環境構築

### ライブラリ

```zsh
  pip install flask aioredis pymysql
```

### docker

#### mysql

```zsh
docker run --name mysql_for_redis -e MYSQL_ROOT_PASSWORD=my-secret-pw -p 3306:3306 -d mysql

docker exec -it [コンテナID] bash

mysql -u root -pmy-secret-pw
CREATE USER app@'%' IDENTIFIED BY 'P@ssw0rd';
GRANT ALL PRIVILEGES on sample.* to app@'%';
CREATE DATABASE sample DEFAULT CHARACTER SET utf8mb4;
USE sample
CREATE TABLE timeline (
     id INT NOT NULL AUTO_INCREMENT,
     name VARCHAR(128) NOT NULL,
     message VARCHAR(140),
     PRIMARY KEY (id)
);
```

#### redis

```zsh
docker run -it --name redis_server -p 6379:6379 --rm redis
```

## Server起動

### 起動準備

```zsh
pip install hypercorn
pip install 'flask[async]'
```

### 起動

```zsh
 hypercorn main:app
```

## Redisで利用している機能

タイムラインはRedisの**List**で管理しています。新しい投稿を`RPUSH`で追加し、最新10件を`LRANGE`で取得します。さらに`EXPIRE`を設定して60秒で自動的に削除されるようにしています。

例:

```python
# 投稿を追加
await redis.rpush('timeline', 'user1: hello')
await redis.expire('timeline', 60)

# 最新10件を取得
messages = await redis.lrange('timeline', 0, 9)
```

