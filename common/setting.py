import redis

# redis 配置

REDIS_ONE = {
    'host': '127.0.0.1',
    'prot': 6379,
    'password': None
}

REDIS_CLIENT_ONE = redis.Redis(host=REDIS_ONE['host'], port=REDIS_ONE['prot'], password=REDIS_ONE['password'])
