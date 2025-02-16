def register_routes(app):
    """Registers all blueprints to the Flask app."""

    from flask_smorest import Api
    from .blueprints.trigger_blueprint import blp as TriggerBlueprint
    from .blueprints.user_blueprint import blp as UserBlueprint
    from .blueprints.event_log_blueprint import blp as EventLogBlueprint
    
    api = Api(app)
    
    api.register_blueprint(UserBlueprint, url_prefix="")
    api.register_blueprint(TriggerBlueprint, url_prefix="")
    api.register_blueprint(EventLogBlueprint, url_prefix="")

    # Configure Swagger UI to include JWT authentication
    api.spec.components.security_scheme(
        "BearerAuth", {
            "type": "http",
            "scheme": "bearer", 
            "bearerFormat": "JWT"
        }
    )
    api.spec.options["security"] = [{"BearerAuth": []}]

    
