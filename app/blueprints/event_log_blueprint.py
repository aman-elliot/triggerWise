from flask import current_app, request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_smorest.pagination import PaginationMetadataSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from redis import Redis
from app.models import EventLog, Trigger
from app.schemas import EventLogSchema
from datetime import datetime, timedelta, timezone
import json

blp = Blueprint("event_log", __name__, description="Event Log Management")
redis_conn = Redis(host='redis_cache')

@blp.route("/events/")
class EventLogList(MethodView):
    @jwt_required()
    @blp.response(200, EventLogSchema(many=True))
    def get(self):
        """Fetch event logs with pagination."""
        try:
            user_id = get_jwt_identity()
            status = request.args.get("status", "active")
            page = int(request.args.get("page", 1))
            per_page = int(request.args.get("per_page", 10))

            # Generate a cache key
            cache_key = f"events:{user_id}:{status}:page:{page}"

            # Check if the data is cached
            cached_data = redis_conn.get(cache_key)
            if cached_data:
                current_app.logger.info("Returning cached event logs.")
                response = json.loads(cached_data)
                return response, 200

            if status == "active":
                two_hours_ago = datetime.now(timezone.utc) - timedelta(hours=2)
                events = EventLog.query.join(Trigger).filter(
                    Trigger.user_id == user_id,
                    EventLog.status == "active",
                    EventLog.created_at >= two_hours_ago
                ).paginate(page=page, per_page=per_page, error_out=False)
            elif status == "archived":
                events = EventLog.query.join(Trigger).filter(
                    Trigger.user_id == user_id,
                    EventLog.status == "archived"
                ).paginate(page=page, per_page=per_page, error_out=False)
            else:
                abort(400, message="Invalid status. Use 'active' or 'archived'.")

            # Serialize the data
            event_schema = EventLogSchema(many=True)
            result = event_schema.dump(events.items)

            # Add pagination metadata
            response = {
                "events": result,
                "pagination": {
                    "total": events.total,
                    "total_pages": events.pages,
                    "first_page": 1,
                    "last_page": events.pages,
                    "page": events.page,
                    "previous_page": events.prev_num if events.has_prev else None,
                    "next_page": events.next_num if events.has_next else None,
                }
            }
    
            # Cache the data for 10 minutes
            redis_conn.set(cache_key, json.dumps(response), ex=600)

            return response, 200

        except Exception as e:
            current_app.logger.error(f"Error fetching event logs: {str(e)}")
            abort(500, message="An error occurred while fetching the event logs.")