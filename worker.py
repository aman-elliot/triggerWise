from rq import Worker
from redis import Redis
from app.tasks import trigger_queue, archive_queue 

redis_conn = Redis(host='redis_cache')

if __name__ == "__main__":

    trigger_worker = Worker(['trigger'], connection=redis_conn)
    archive_worker = Worker(['archive'], connection=redis_conn)
    
    trigger_worker.work()
    archive_worker.work()