import aioredis
from quart import Quart, request, jsonify, render_template
import pymysql

app = Quart(__name__)

# RedisおよびMySQL接続設定
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
MYSQL_HOST = '127.0.0.1'
MYSQL_USER = 'app'
MYSQL_PASSWORD = 'P@ssw0rd'
MYSQL_DB = 'voting'


@app.before_serving
async def startup():
    app.redis = await aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")
    app.mysql = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


@app.after_serving
async def shutdown():
    await app.redis.close()
    app.mysql.close()


async def register_with_redis(voter, candidate):
  await app.redis.sadd(candidate, voter)


async def register_with_mysql(voter, candidate):
  with app.mysql.cursor() as cursor:
    sql = "INSERT INTO votes (candidate, voter) VALUES (%s, %s)"
    cursor.execute(sql, (candidate, voter))
  app.mysql.commit()


async def get_candidates_from_redis():
  cursor = 0
  candidates = set()
  while True:
    cursor, keys = await app.redis.scan(cursor=cursor, match='candidate:*')
    print(cursor, keys)
    candidates.update(k.decode() for k in keys)
    if cursor == 0:
      break
  return candidates

async def get_candidates_from_mysql():
  candidates = set()
  with app.mysql.cursor() as cursor:
    cursor.execute("SELECT candidate, voter FROM votes")
    results = cursor.fetchall()
    for row in results:
      await register_with_redis(row['candidate'], row['voter'])
      candidates.add(row['candidate'])
  return candidates

@app.route('/')
async def index():
  return await render_template('index.html')


@app.route('/vote', methods=['POST'])
async def vote():
  form = await request.get_json()
  candidate = form.get('candidate')
  print(candidate)
  voter = form.get('voter')
  print(voter)
  if not candidate or not voter:
    return jsonify({}), 200

  if candidate and voter:
    await register_with_mysql(voter, candidate)
    await register_with_redis(voter, candidate)

  candidates = await get_candidates_from_redis()
  if len(candidates) <= 1:
    candidates = await get_candidates_from_mysql()

  counts = {}
  for cand in candidates:
    counts[cand] = await app.redis.scard(cand)
  
  return jsonify(dict(sorted(counts.items())))


if __name__ == '__main__':
    app.run(debug=True)