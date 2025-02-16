#!/bin/sh

# echo "Waiting for PostgreSQL to start..."
# while ! nc -z db 5432; do
#   sleep 1
# done
# echo "PostgreSQL started!"

# Run database migrations
echo "Running database migrations..."
flask db upgrade

# Start RQ workers for specific queues with options
echo "Starting Redis Queue workers..."

# Worker for 'trigger' queue with scheduler
rq worker trigger  &

# Worker for 'alert' queue without scheduler
rq worker archive &

# Start the Flask app
echo "Starting Flask app..."
exec flask run --host=0.0.0.0
