import aioredis
from quart import Quart, render_template


app = Quart(__name__)


# RedisおよびMySQL接続設定
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
STREAM_MAX_LEN = 1000


@app.before_serving
async def startup():
    app.redis = await aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")


@app.route('/')
async def index():
    return await render_template('index.html')


async def read_message(websocket: Websocket, join_info: dict):
    """
    WebSocketでメッセージを受信する
    """
    connected = True
    is_first_message = True
    stream_id = '$'
    while connected:
        count = 1 if is_first_message else 100
        results = await app.redis.xread(
            streams={join_info['room']: stream_id},
            count=count,
            block=100000,
        )
        for room, events in results:
            if join_info['room'] != room.decode('utf-8'):
                continue

            for event_id, event in events:
                now = datetime.datetime.now()

                # チャンネルに参加しているユーザーに通知
                msg_decoded = event[b'msg'].decode("utf-8")
                await websocket.send_text(f'{now.strftime("%Y-%m-%d %H:%M:%S")} {msg_decoded}')
              
                stream_id = event_id
                if is_first_message:
                    is_first_message = False
                    
        connected = False


async def write_message(websocket: Websocket, join_info: dict):
    """
    WebSocketでメッセージを送信する
    """
    await notify(join_info, 'joined')

    connected = True
    while connected:
        try:
            message = await websocket.receive_text()
            await app.redis.xadd(join_info['room'], {'username': join_info['username'], 'msg': message}, id=b'*', maxlen=STREAM_MAX_LEN)
        except:
            # ブラウザを閉じるなど、WebSocketが切断された場合
            await notify(join_info, 'left')
            await app.redis.close()
            connected = False


async def notify(join_info: dict, action: str):
    """
    チャンネルに参加しているユーザーに通知を送信する
    """
    now = datetime.datetime.now()
    message = f'{now.strftime("%Y-%m-%d %H:%M:%S")} {join_info["username"]} has {action}.'
    await app.redis.xadd(join_info['room'], {'msg': message}, id=b'*', maxlen=STREAM_MAX_LEN)


async def get_joininfo(username: str = None, room: str = None):
    """
    WebSocket接続時に必要な情報を取得する
    """
    return {"username": username, "room": room}


async def websocket_endpoint(websocket: Websocket, join_info: dict = Depends(get_joininfo)):
    """
    WebSocketによる通信に使用するエンドポイント
    """
    await websocket.accept()
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    # メッセージの読み取りと書き込みを同時に実行
    await asyncio.gather(
        read_message(websocket, join_info),
        write_message(websocket, join_info)
    )


if __name__ == '__main__':
    app.run(debug=True)