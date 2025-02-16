from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Str(required=True, validate=validate.Email())
    password = fields.Str(required=True, load_only=True)  # Only for input, not output
    triggers = fields.List(fields.Nested('TriggerSchema', exclude=('user',)))
    created_at = fields.DateTime(dump_only=True)

class TriggerSchema(Schema):
    id = fields.Int(dump_only=True)
    type = fields.Str(required=True)
    schedule_time = fields.DateTime(allow_none=True)
    interval = fields.Int(allow_none=True)
    recurrence = fields.Bool(allow_none=True)
    api_endpoint = fields.Str(allow_none=True)
    api_payload = fields.Dict(allow_none=True)
    user_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    deleted_at = fields.DateTime(allow_none=True)

# Schema for Creating a Trigger
class TriggerCreateSchema(Schema):
    type = fields.Str(required=True)
    schedule_time = fields.DateTime(required=False)
    interval = fields.Int(required=False)
    recurrence = fields.Bool(required=False)
    api_endpoint = fields.Str(required=False)
    api_payload = fields.Dict(required=False)

# Schema for Updating a Trigger
class TriggerUpdateSchema(Schema):
    schedule_time = fields.DateTime(required=False)
    interval = fields.Int(required=False)
    recurrence = fields.Bool(required=False)
    api_endpoint = fields.Str(required=False)
    api_payload = fields.Dict(required=False)

# Schema for Testing a Trigger
class TriggerTestSchema(Schema):
    type = fields.Str(required=True)
    schedule_time = fields.DateTime(required=False)
    api_endpoint = fields.Str(required=False)
    api_payload = fields.Dict(required=False)

class EventLogSchema(Schema):
    id = fields.Int(dump_only=True)
    trigger_id = fields.Int(required=True)
    payload = fields.Dict(allow_none=True)
    status = fields.Str(default="active")
    created_at = fields.DateTime(dump_only=True)
    archived_at = fields.DateTime(allow_none=True)
    deleted_at = fields.DateTime(allow_none=True)

class UserRegistrationSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Str(required=True, validate=validate.Email())
    password = fields.Str(required=True, validate=validate.Length(min=6, error="Password must be at least 6 characters long."), load_only=True)

class UserLoginSchema(Schema):
    email = fields.Str(required=True, validate=validate.Email())
    password = fields.Str(required=True)
    