from pymongo import MongoClient, errors as mongo_errors
import logging
import config
from utils import run_rsync
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@contextmanager
def mongo_connection():
    uri = config.MONGODB_URI
    client = None
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        logger.info('Connected successfully to MongoDB')
        yield client
    except mongo_errors.ServerSelectionTimeoutError:
        logger.error('Failed to connect to MongoDB: Server selection timeout.')
        raise
    except mongo_errors.ConnectionError:
        logger.error('Failed to connect to MongoDB: Connection error.')
        raise
    except Exception as err:
        logger.error(f'An unexpected error occurred: {err}')
        raise
    finally:
        if client:
            client.close()
            logger.info('Connection to MongoDB closed.')

def fetch_members_with_role(database):
    try:

        collection = database[config.COLLECTION_NAME]
        query = {'discord_roles_ids': config.ROLE_ID}
        data = list(collection.find(query))

        if not data:
            logger.info(f'No data found for role: {config.ROLE_ID}')
            return []

        return data

    except mongo_errors.PyMongoError as err:
        logger.error(f'MongoDB error during member fetch: {err}')
        return []
    except Exception as err:
        logger.error(f'An error occurred during member fetch: {err}')
        return []

def fetch_reward_needed_points(database, category='seeding_tracker'):
    try:
        # Access the 'configs' collection
        collection = database['configs']
        
        # Query to find the configuration document by category
        query = {'category': category}
        config_doc = collection.find_one(query)
        
        if not config_doc:
            logger.info(f'No configuration found for category: {category}')
            return None
        
        # Extract the 'reward_needed_time' from the config
        reward_needed_time = config_doc.get('config', {}).get('reward_needed_time')
        
        if not reward_needed_time:
            logger.info('No reward_needed_time found in configuration')
            return None
        
        # Extract 'value' and 'option'
        value = reward_needed_time.get('value')
        option = reward_needed_time.get('option')
        
        if value is None or option is None:
            logger.info('Invalid reward_needed_time configuration: Missing value or option')
            return None
        
        # Calculate the total time in milliseconds
        total_time_ms = value * option
        
        # Convert milliseconds to minutes (1 minute = 60,000 ms)
        total_time_minutes = total_time_ms / 60000
        
        # Assuming 1 point is gained per minute
        reward_points = int(total_time_minutes)
        
        logger.info(f'Points needed for reward: {reward_points}')
        return reward_points
    
    except mongo_errors.PyMongoError as err:
        logger.error(f'MongoDB error during config fetch: {err}')
        return None
    except Exception as err:
        logger.error(f'An unexpected error occurred during config fetch: {err}')
        return None

def perform_database_operations():
    try:
        if config.USE_DB_CLONE:
            run_rsync()

        with mongo_connection() as client:
            database = client[config.DATABASE_NAME]

            members = fetch_members_with_role(database)
            logger.info(f'Fetched {len(members)} members with role {config.ROLE_ID}')

            reward_points = fetch_reward_needed_points(database)
            if reward_points is not None:
                logger.info(f'Calculated points: {reward_points}')
            else:
                logger.info('Points needed for reward not found or could not be calculated.')

            return {
                'members': members,
                'reward_points': reward_points
            }

    except Exception as e:
        logger.error(f'An error occurred during database operations: {e}')
        return {}
