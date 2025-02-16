from flask import current_app, request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from app.models import Trigger
from app import db
from app.schemas import TriggerCreateSchema, TriggerSchema, TriggerUpdateSchema, TriggerTestSchema
from datetime import datetime, timedelta, timezone

from app.tasks import execute_api_trigger, execute_scheduled_trigger, execute_test_scheduled_trigger, trigger_queue

blp = Blueprint("triggers", __name__, description="Trigger Management")

# Create a Trigger
@blp.route("/triggers/")
class TriggerList(MethodView):
    @jwt_required()
    @blp.arguments(TriggerCreateSchema)
    @blp.response(201, TriggerSchema)
    def post(self, data):
        """Create a new trigger (Scheduled or API-based)."""
        try:
            user_id = get_jwt_identity()
            trigger = Trigger(user_id=user_id, **data)

            db.session.add(trigger)
            db.session.commit()
            
            if trigger.type == "scheduled":
                if trigger.schedule_time:
                    trigger_queue.enqueue_at(trigger.schedule_time, execute_scheduled_trigger, trigger.id, trigger.recurrence)
                    current_app.logger.info(f"Trigger scheduled for {trigger.schedule_time}")
                elif trigger.interval:
                    execution_time = datetime.now(timezone.utc) + timedelta(minutes=trigger.interval)
                    trigger_queue.enqueue_at(execution_time, execute_scheduled_trigger, trigger.id, trigger.recurrence)
                    current_app.logger.info(f"Trigger scheduled at Interval {trigger.interval} minutes.")
                else:
                    abort(400, message="For scheduled triggers, provide either schedule_time or interval.")
            elif trigger.type == "api":
                execute_api_trigger(trigger.id, trigger.api_endpoint, trigger.api_payload)
            
            return trigger
        
        except Exception as e:
            current_app.logger.error(f"Error saving trigger: {str(e)}")
            abort(500, message="An error occurred while saving the trigger.")

        
    # View All Triggers
    @jwt_required()
    @blp.response(200, TriggerSchema(many=True))
    def get(self):
        """Retrieve all triggers created by the user."""
        try:
            user_id = get_jwt_identity()
            return Trigger.query.filter_by(user_id=user_id).all()
        
        except Exception as e:
            current_app.logger.error(f"Error retrieving triggers: {str(e)}")
            abort(500, message="An error occurred while retrieving the triggers.")

# View, Update, and Delete a Trigger
@blp.route("/triggers/<int:trigger_id>")
class TriggerResource(MethodView):
    @jwt_required()
    @blp.response(200, TriggerSchema)
    def get(self, trigger_id):
        """Retrieve details of a specific trigger."""
        try:
            trigger = Trigger.query.get_or_404(trigger_id)
            return trigger
        
        except Exception as e:
            current_app.logger.error(f"Error retrieving trigger: {str(e)}")
            abort(500, message="An error occurred while retrieving the trigger.")

    @jwt_required()
    @blp.arguments(TriggerUpdateSchema)
    @blp.response(200, TriggerSchema)
    def put(self, data, trigger_id):
        """Update an existing trigger."""
        try:
            trigger = Trigger.query.get_or_404(trigger_id)
            for key, value in data.items():
                setattr(trigger, key, value)

            db.session.commit()
            return trigger
        
        except Exception as e:
            current_app.logger.error(f"Error updating trigger: {str(e)}")
            abort(500, message="An error occurred while updating the trigger.")

    @jwt_required()
    def delete(self, trigger_id):
        """Delete a trigger (but keep event logs)."""
        try:
            trigger = Trigger.query.get_or_404(trigger_id)
            db.session.delete(trigger)
            db.session.commit()
            return {"message": "Trigger deleted successfully"}, 200
        
        except Exception as e:
            current_app.logger.error(f"Error deleting trigger: {str(e)}")
            abort(500, message="An error occurred while deleting the trigger.")

# Test a Trigger (Manually Fire Once)
@blp.route("/triggers/test/")
class TriggerTest(MethodView):
    @jwt_required()
    @blp.arguments(TriggerTestSchema)
    @blp.response(200, TriggerSchema)
    def post(self, data):
        """Manually test a trigger (Scheduled or API) without saving it."""
        try:
            user_id = get_jwt_identity()
            trigger = Trigger(user_id=user_id, **data)

            # not saving the trigger to the database
            # but we can still log the event            
            if trigger.type == "scheduled":
                execution_time = datetime.now(timezone.utc) + timedelta(minutes=trigger.interval)
                trigger_queue.enqueue_at(execution_time, execute_test_scheduled_trigger, trigger.id, trigger.recurrence)

            elif trigger.type == "api":
                execute_api_trigger(trigger.id, trigger.api_endpoint, trigger.api_payload)

            else:
                abort(400, message="Invalid trigger type")

            return trigger
        
        except Exception as e:
            current_app.logger.error(f"Error saving trigger: {str(e)}")
            abort(500, message="An error occurred while saving the trigger.")
        
