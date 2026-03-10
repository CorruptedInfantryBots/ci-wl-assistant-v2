#!/usr/bin/env python

import time
from datetime import datetime, timedelta
import logging
import signal
import sys
import threading
import os
from logging.handlers import RotatingFileHandler
import config
from database.mongodb import perform_database_operations
from database.sql import connect_to_sql
from role_manager import RoleManager
from pymongo import errors as mongo_errors
import mysql.connector
from mysql.connector import Error as mysql_errors
from utils import initialize_database, run_rsync

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure the log directory exists
log_dir = os.path.dirname(config.LOG_FILE)
if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Add a rotating file handler to manage log file size
handler = RotatingFileHandler(config.LOG_FILE, maxBytes=config.LOG_MAX_BYTES, backupCount=config.LOG_BACKUP_COUNT)
logger.addHandler(handler)

# Initialize the database and create the timers table if it doesn't exist
initialize_database()

# Initialize RoleManager
role_manager = RoleManager(config.GUILD_ID)

# Create a shutdown event
shutdown_event = threading.Event()

def signal_handler(signum, frame):
    logger.info(f"Signal {signum} received, shutting down gracefully.")
    shutdown_event.set()

# Register signal handlers for graceful shutdown
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def handle_seeding_points(members_data, reward_points):
    try:
        timers = role_manager.load_timers()

        users_to_assign = []
        users_removed = []
        users_with_timers = []
        users_unchanged = []

        for doc in members_data:
            try:
                discord_user_id = doc.get('discord_user_id')
                
                # Skip invalid members
                if not discord_user_id:
                    logger.warning(f"Skipping member with missing discord_user_id: {doc.get('_id', 'unknown')}")
                    continue
                    
                user_roles = doc.get('discord_roles_ids', [])
                seeding_points = doc.get('seeding_points', 0)

                # Check if a timer already exists for this user
                existing_timer = next((t for t in timers if t[0] == discord_user_id), None)
                expiration_time = datetime.fromisoformat(existing_timer[2]) if existing_timer else None

                if seeding_points > reward_points and config.SEED_ROLE_ID not in user_roles:
                    users_to_assign.append(discord_user_id)
                    role_manager.add_role(discord_user_id, config.SEED_ROLE_ID)
                    if existing_timer:
                        role_manager.cancel_timer(discord_user_id)
                elif seeding_points <= reward_points and config.SEED_ROLE_ID in user_roles:
                    if expiration_time and datetime.now() > expiration_time:
                        role_manager.remove_role(discord_user_id, config.SEED_ROLE_ID, remove_timer=True)
                        logger.debug(f"Timer for user {discord_user_id} has expired, role removed.")
                        users_removed.append(discord_user_id)
                    elif not existing_timer:
                        users_with_timers.append(discord_user_id)
                        role_manager.start_timer(discord_user_id, config.SEED_ROLE_ID)
                    else:
                        users_with_timers.append(discord_user_id)
                        expiration_time_str = existing_timer[2] if existing_timer else 'N/A'
                        logger.debug(f"Timer already exists for user {discord_user_id}, expiring at {expiration_time_str}, skipping.")
                else:
                    users_unchanged.append(discord_user_id)
                    
            except Exception as inner_err:
                logger.error(f'Error processing member {doc.get("_id", "unknown")}: {inner_err}')
                continue

        logger.info(f"Processed {len(members_data)} users for seeding points.")
        logger.info(f"{len(users_to_assign)} users had roles assigned: {users_to_assign}")
        logger.info(f"{len(users_removed)} users were removed: {users_removed}")
        logger.info(f"{len(users_with_timers)} users have timers: {users_with_timers}")
        logger.info(f"{len(users_unchanged)} users were unchanged: {users_unchanged}")

    except Exception as err:
        logger.error(f'An error occurred in handle_seeding_points: {err}')

def handle_hours_played(members_data):
    try:
        # Connect to SQL database
        sql_cnx = connect_to_sql()
        cursor = sql_cnx.cursor(dictionary=True)

        # Calculate the time window for the past 'n' weeks
        weeks_ago = datetime.now() - timedelta(weeks=config.HOURS_PLAYED_WEEKS)

        # Query to get total hours played in the past week per user
        query = """
        SELECT
            steamID,
            IFNULL(SUM(TIMESTAMPDIFF(SECOND, joinTime, leaveTime)) / 3600, 0) AS hours_played
        FROM
            ActivityTracker_PlayerSessions
        WHERE
            joinTime >= %s
        GROUP BY
            steamID
        """

        cursor.execute(query, (weeks_ago,))
        hours_data = cursor.fetchall()

        if not hours_data:
            logger.info('No player activity data found for the past week.')
            return

        # Map Steam IDs to hours played
        steam_hours_map = {row['steamID']: row['hours_played'] for row in hours_data}

        users_to_assign = []
        users_removed = []
        users_unchanged = []

        for user in members_data:
            try:
                discord_user_id = user.get('discord_user_id')
                
                # Skip invalid members
                if not discord_user_id:
                    logger.warning(f"Skipping member with missing discord_user_id: {user.get('_id', 'unknown')}")
                    continue
                
                steam_id = user.get('steamid64')

                if not steam_id:
                    logger.debug(f"User {discord_user_id} does not have a linked Steam ID.")
                    continue

                user_roles = user.get('discord_roles_ids', [])
                hours_played = steam_hours_map.get(steam_id, 0) # Defaults to 0 if not found

                if hours_played >= config.HOURS_THRESHOLD and config.ACTIVITY_ROLE_ID not in user_roles:
                    users_to_assign.append(discord_user_id)
                    role_manager.add_role(discord_user_id, config.ACTIVITY_ROLE_ID)
                elif hours_played < config.HOURS_THRESHOLD and config.ACTIVITY_ROLE_ID in user_roles:
                    users_removed.append(discord_user_id)
                    role_manager.remove_role(discord_user_id, config.ACTIVITY_ROLE_ID)
                else:
                    users_unchanged.append(discord_user_id)
                    
            except Exception as inner_err:
                logger.error(f'Error processing member {user.get("_id", "unknown")}: {inner_err}')
                continue

        logger.info(f"Processed {len(members_data)} users for hours played.")
        logger.info(f"{len(users_to_assign)} users had roles assigned: {users_to_assign}")
        logger.info(f"{len(users_removed)} users were removed: {users_removed}")
        logger.info(f"{len(users_unchanged)} users were unchanged: {users_unchanged}")

    except mysql_errors as err:
        logger.error(f'SQL error in handle_hours_played: {err}')
    except mongo_errors.PyMongoError as err:
        logger.error(f'MongoDB error in handle_hours_played: {err}')
    except Exception as err:
        logger.error(f'An error occurred in handle_hours_played: {err}')
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'sql_cnx' in locals():
            sql_cnx.close()
            logger.info('Connection to SQL database closed')

def deduplicate_members_data(members_data):
    unique_members = {}
    
    for member in members_data:
        discord_id = member.get('discord_user_id')
        if not discord_id:
            continue
            
        # If this discord_id hasn't been seen yet, add it
        if discord_id not in unique_members:
            unique_members[discord_id] = member
        # If we already have this user, prefer the one with latest_seeding_activity
        elif 'latest_seeding_activity' in member and 'latest_seeding_activity' not in unique_members[discord_id]:
            unique_members[discord_id] = member
        # If both have latest_seeding_activity, prefer the newer one
        elif ('latest_seeding_activity' in member and 'latest_seeding_activity' in unique_members[discord_id] and
              member['latest_seeding_activity'] > unique_members[discord_id]['latest_seeding_activity']):
            unique_members[discord_id] = member
            
    return list(unique_members.values())

def main():
    health_file = 'data/health.check'
    try:
        with open(health_file, 'w') as f:
            f.write(str(time.time()))
    except Exception as e:
        logger.error(f'Failed to update health check file: {e}')

    # Fetch data from mongodb
    db_results = perform_database_operations()
    
    # Extract variables from the returned dictionary
    members_data = db_results.get('members', [])
    reward_points = db_results.get('reward_points', 115)

    # Deduplicate members data
    deduplicated_members = deduplicate_members_data(members_data)

    logger.info(f'Number of Members (before deduplication): {len(members_data)}')
    logger.info(f'Number of Members (after deduplication): {len(deduplicated_members)}')
    logger.info(f'Points Needed for Reward: {reward_points}')

    # Handle seeding points and roles
    handle_seeding_points(deduplicated_members, reward_points)

    # Handle hours played and roles
    handle_hours_played(deduplicated_members)

if __name__ == '__main__':

    try:
        while not shutdown_event.is_set():
            main()
            # Wait for 180 seconds or until shutdown_event is set
            shutdown_event.wait(timeout=config.SLEEP_DURATION)
    except Exception as e:
        logger.error(f'An error occurred: {e}')
    finally:
        logger.info('Program is exiting.')
