import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB 
MONGODB_USERNAME = os.getenv('MONGODB_USERNAME')
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD')
MONGODB_HOST = os.getenv('MONGODB_HOST')
MONGODB_PORT = os.getenv('MONGODB_PORT')
MONGODB_URI = f'mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}'
DATABASE_NAME = 'admin'
COLLECTION_NAME = 'players'

# Flag to determine if cloning is needed
USE_DB_CLONE = os.getenv('USE_DB_CLONE', 'False').lower() == 'true'
# Paths for rsync
MONGODB_MAIN_DATA_PATH = os.getenv('MONGODB_MAIN_DATA_PATH')
MONGODB_CLONE_DATA_PATH = os.getenv('MONGODB_CLONE_DATA_PATH')
MONGODB_CLONE_CONTAINER_NAME = os.getenv('MONGODB_CLONE_CONTAINER_NAME')

# SQL Database 
SQL_HOST = os.getenv('SQL_HOST')
SQL_PORT = int(os.getenv('SQL_PORT'))
SQL_USERNAME = os.getenv('SQL_USERNAME')
SQL_PASSWORD = os.getenv('SQL_PASSWORD')
SQL_DATABASE = os.getenv('SQL_DATABASE')

# API 
API_URL = os.getenv('API_URL')

# Discord 
GUILD_ID = os.getenv('GUILD_ID')
ROLE_ID = os.getenv('ROLE_ID')
SEED_ROLE_ID = os.getenv('SEED_ROLE_ID')
ACTIVITY_ROLE_ID = os.getenv('ACTIVITY_ROLE_ID') 

# SEEDING Thresholds
HOURS_THRESHOLD = float(os.getenv('HOURS_THRESHOLD'))

# Time window for calculating hours played
HOURS_PLAYED_WEEKS = int(os.getenv('HOURS_PLAYED_WEEKS'))

# Timer 
TIMER_DURATION = int(os.getenv('TIMER_DURATION', 1209600))  # Default to 2 weeks

SLEEP_DURATION = int(os.getenv('SLEEP_DURATION', 60)) # Default to 1 minute

# Logging 
LOG_FILE = os.getenv('LOG_FILE', 'app.log')
LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', '1000000'))
LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '5'))
