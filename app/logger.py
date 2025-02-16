import logging
from logging.handlers import TimedRotatingFileHandler
import sys
import os

def setup_logger(app):
    """Sets up the logger for the application with daily log rotation."""
    log_level = logging.DEBUG if app.config['FLASK_ENV'] == "development" else logging.INFO

    # Create a logger object
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Create a console handler for streaming logs to stdout
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(log_level)

    # Create a file handler for daily rotation
    log_directory = "logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    
    log_file = os.path.join(log_directory, "app.log")

    # Set up timed rotating file handler (rotate every day)
    fh = TimedRotatingFileHandler(
        log_file, when="midnight", interval=1, backupCount=7  # Keeps last 7 days of logs
    )
    fh.setLevel(logging.INFO)

    # Create a formatter and add it to both handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    # Attach logger to Flask's app object
    app.logger = logger
