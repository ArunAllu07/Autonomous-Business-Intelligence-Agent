import os

import redis
from dotenv import load_dotenv


load_dotenv()


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))


redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
)


def check_redis_connection() -> bool:
    try:
        return bool(redis_client.ping())
    except redis.RedisError:
        return False


def set_value(key: str, value: str, ttl: int | None = None) -> bool:
    try:
        redis_client.set(key, value, ex=ttl)
        return True
    except redis.RedisError:
        return False


def get_value(key: str) -> str | None:
    try:
        return redis_client.get(key)
    except redis.RedisError:
        return None


def delete_value(key: str) -> bool:
    try:
        return bool(redis_client.delete(key))
    except redis.RedisError:
        return False