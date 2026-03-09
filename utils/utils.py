import sqlite3
import subprocess
import logging
import os
import re
import config

logger = logging.getLogger(__name__)

def execute_db_query(query, args=()):
    conn = sqlite3.connect('data/timers.db')
    c = conn.cursor()
    c.execute(query, args)
    conn.commit()
    conn.close()

def initialize_database():
    """
    Initializes the data/timers.db database and creates the timers table if it doesn't exist.
    """
    if not os.path.exists('data/timers.db'):
        logger.info('Database data/timers.db does not exist. Creating a new one.')
    else:
        logger.info('Database data/timers.db already exists.')

    # Create the timers table if it doesn't exist
    execute_db_query('''
    CREATE TABLE IF NOT EXISTS timers (
        discord_user_id TEXT PRIMARY KEY,
        role_id TEXT,
        expiration_time TEXT,
        start_time TEXT
    )
    ''')
    logger.info('Timers table ensured to exist in data/timers.db.')
    
def is_valid_container_name(name):
    # Allow alphanumeric characters, underscores, and hyphens
    pattern = re.compile(r'^[a-zA-Z0-9_-]+$')
    return pattern.match(name) is not None

def is_valid_path(path):
    # Check if path is absolute and does not contain '..'
    return os.path.isabs(path) and '..' not in os.path.normpath(path)

def run_command(command):
    """
    Helper function to run a shell command.
    """
    try:
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with error: {e.stderr}")
        raise
def run_rsync():
    """
    Stops the MongoDB clone container, runs the rsync command to synchronize the MongoDB data from the original to the clone, and then restarts the container.
    """
    container_name = config.MONGODB_CLONE_CONTAINER_NAME
    main_data_path = config.MONGODB_MAIN_DATA_PATH
    clone_data_path = config.MONGODB_CLONE_DATA_PATH

    # Validate container name
    if not is_valid_container_name(container_name):
        raise ValueError(f"Invalid container name: {container_name}")

    # Validate paths
    if not is_valid_path(main_data_path):
        raise ValueError(f"Invalid main data path: {main_data_path}")

    if not is_valid_path(clone_data_path):
        raise ValueError(f"Invalid clone data path: {clone_data_path}")

    # Stop MongoDB Docker container
    logger.info("Stopping MongoDB clone container...")
    run_command(['docker', 'stop', container_name])

    # Run rsync
    try:
        logger.info("Running rsync to synchronize MongoDB data...")
        result = run_command(
            [
                'rsync', '-avz', '--delete',
                f"{main_data_path}/",
                f"{clone_data_path}/"
            ]
        )
        logger.debug(f"rsync output:\n{result}")
    finally:
        # Start MongoDB Docker container
        logger.info("Starting MongoDB clone container...")
        run_command(['docker', 'start', container_name])