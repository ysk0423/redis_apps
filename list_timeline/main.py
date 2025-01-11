import aioredis
from flask import Flask, request, render_template, g
from flask.json import jsonify
import pymysql

app = Flask(__name__)

# RedisおよびMySQL接続設定
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
MYSQL_HOST = '127.0.0.1'
MYSQL_USER = 'app'
MYSQL_PASSWORD = 'P@ssw0rd'
MYSQL_DB = 'sample'


async def get_redis_connection():
    return await aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")


def get_mysql_connection():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


@app.before_request
async def before_request():
  g.redis = await get_redis_connection()
  g.mysql = get_mysql_connection()


@app.teardown_request
async def teardown_request(exception):
    if hasattr(g, 'redis'):
      await g.redis.close()
    if hasattr(g, 'mysql'):
      g.mysql.close()


async def register_with_redis(key, user, message):
  async with g.redis.pipeline() as pipe:
     await pipe.rpush(key, f"{user}: {message}")
     await pipe.expire(key, 60)
     await pipe.execute()


async def register_with_mysql(user, message):
  with g.mysql.cursor() as cursor:
    sql = "INSERT INTO timeline (name, message) VALUES (%s, %s)"
    cursor.execute(sql, (user, message))
  g.mysql.commit()


async def get_messages(key):
  messages = await g.redis.lrange(key, 0, 9)
  decoded_messages = [message.decode('utf-8') for message in messages] 
  if not decoded_messages:
    with g.mysql.cursor() as cursor:
      sql = "SELECT name, message FROM timeline ORDER BY id DESC LIMIT 10"
      cursor.execute(sql)
      results = cursor.fetchall()
      for row in results:
        record = f"{row['name']}: {row['message']}"
        decoded_messages.append(record)
        await g.redis.rpush(key, record)
      await g.redis.expire(key, 60)
  return decoded_messages


@app.route('/')
def index():
  return render_template('timeline.html')


@app.route('/timeline', methods=['POST'])
async def timeline():
  user = request.form.get('user')
  message = request.form.get('message')
  is_first = request.form.get('isFirst') == 'true'

  key = 'timeline'

  if not is_first:
     await register_with_redis(key, user, message)
     await register_with_mysql(user, message)
  
  messages = await get_messages(key)
  return jsonify(messages)


if __name__ == '__main__':
    app.run(debug=True)