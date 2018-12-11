import config
import redis

from rq import Worker, Queue, Connection
listen = ['htmlizer']

if __name__ == '__main__':
    conn = redis.from_url(config.REDIS_URL)
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()