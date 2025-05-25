# Redisストリームを使ったリアルタイムチャット

## 動作環境

- python3.9

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

#### redis

```zsh
docker run -it --name chat_server -p 6379:6379 --rm redis
```

## Server起動

```zsh
 poetry run python main.py
```

## 実装機能

- チャットメッセージ送信
- チャットメッセージ取得
- チャットルーム入室
- チャットルーム退室
- チャットルーム入室通知
- チャットルーム退室通知
