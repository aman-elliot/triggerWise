from rq import Queue
from redis import Redis
from datetime import datetime, timezone, timedelta
import requests
from app import db
from app.models import EventLog, Trigger
from flask import current_app

redis_conn = Redis(host='redis_cache')
trigger_queue = Queue('trigger', connection=redis_conn)
archive_queue = Queue('archive', connection=redis_conn)

def execute_scheduled_trigger(trigger_id, recurrence=False):
    try:
        trigger = Trigger.query.get(trigger_id)
        if not trigger:
            return

        log_event(trigger.id)

        if recurrence:  # Recur if enabled
            if trigger.schedule_time:
                next_execution = trigger.schedule_time + timedelta(days=1)
            else:
                next_execution = datetime.now(timezone.utc) + timedelta(minutes=trigger.interval)
            trigger_queue.enqueue_at(next_execution, execute_scheduled_trigger, trigger_id, recurrence)

    except Exception as e:
        current_app.logger.error(f"Error executing scheduled trigger: {str(e)}")

def execute_api_trigger(trigger_id, api_endpoint, api_payload):
    try:
        api_response = requests.post(api_endpoint, json=api_payload)
        log_event(trigger_id, api_response)

    except Exception as e:
        current_app.logger.error(f"Error executing API trigger: {str(e)}")

def execute_test_scheduled_trigger(trigger_id):
    try:
        trigger = Trigger.query.get(trigger_id)
        if not trigger:
            return

        log_event(trigger.id, status='test')

    except Exception as e:
        current_app.logger.error(f"Error executing scheduled trigger: {str(e)}")

def execute_test_api_trigger(trigger_id, api_endpoint, api_payload):
    try:
        api_response = requests.post(api_endpoint, json=api_payload)
        log_event(trigger_id, api_response, status='test')

    except Exception as e:
        current_app.logger.error(f"Error executing API trigger: {str(e)}")

def log_event(trigger_id, payload=None, response=None, status='active'):
    try:
        event = EventLog(trigger_id=trigger_id, response=response, status=status)
        db.session.add(event)
        db.session.commit()
        current_app.logger.info(f"-------------- Event logged for trigger {trigger_id} ----------------")

        # Invalidate the cache for this user's event logs
        user_id = Trigger.query.get(trigger_id).user_id
        delete_keys_by_pattern(f"events:{user_id}:*")

        current_app.logger.info(f"Event logged and cache invalidated for user {user_id}.")

    except Exception as e:
        current_app.logger.error(f"Error logging event: {str(e)}")

def delete_keys_by_pattern(pattern, count=100):
    """
    Deletes keys from Redis that match the specified pattern.

    Parameters:
    - redis_client: A Redis client instance (e.g., redis.StrictRedis)
    - pattern: A pattern to match keys (e.g., "prefix:*")
    - count: Number of keys to return per scan iteration (default: 100)
    """
    cursor = 0
    while True:
        cursor, keys = redis_conn.scan(cursor=cursor, match=pattern, count=count)
        if keys:
            redis_conn.delete(*keys)
        if cursor == 0:
            break

def archive_and_delete_event():
    try:
        # Archive events older than 2 hours but less than 48 hours
        events = EventLog.query.filter(EventLog.created_at <= datetime.now(timezone.utc) - timedelta(hours=2),
                                       EventLog.status == "active").all()

        for event in events:
            event.status = "archived"
            event.archived_at = datetime.now(timezone.utc)
            db.session.commit()

        # Delete events older than 48 hours
        events_to_delete = EventLog.query.filter(EventLog.created_at <= datetime.now(timezone.utc) - timedelta(hours=48),
                                                 EventLog.status == "archived").all()

        for event in events_to_delete:
            db.session.delete(event)

        db.session.commit()

    except Exception as e:
        current_app.logger.error(f"Error during event archival/deletion: {str(e)}")

def schedule_event_archival_and_deletion():
    """Enqueue the task for event archival and deletion"""
    archive_queue.enqueue_in(timedelta(minutes=2), archive_and_delete_event)