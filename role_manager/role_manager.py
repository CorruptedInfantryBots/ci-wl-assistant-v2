import logging
from ratelimiter import RateLimiter
from threading import Lock
import requests
import config
from utils import execute_db_query, get_api_client
from datetime import datetime, timedelta
import sqlite3

logger = logging.getLogger(__name__)

class RoleManager:
    def __init__(self, guild_id):
        # Initialize the API client using the factory function
        self.api_client = get_api_client()

    def add_role(self, user_id, role_id):
        logger.debug(f"Assigning role {role_id} to user {user_id} via API client.")
        self.api_client.add_role(config.GUILD_ID, user_id, role_id)
        # Remove any existing timer for the user, as they are getting the role back
        self.cancel_timer(user_id)

    def remove_role(self, user_id, role_id, remove_timer=False):
        
        self.api_client.remove_role(config.GUILD_ID, user_id, role_id)

        if remove_timer:
            # Retrieve the start time of the timer before removing the role.
            timer_info = self.get_timer_info(user_id)   
            start_time = timer_info['start_time'] if timer_info else 'No timer found'

            logger.debug(f"Removing role {role_id} from user {user_id} via API client with timestamp {start_time}.")
            self.api_client.remove_role(config.GUILD_ID, user_id, role_id, start_time)
            # Delete the timer from the database only if remove_timer is True
            execute_db_query('DELETE FROM timers WHERE discord_user_id = ?', (user_id,))

    def start_timer(self, user_id, role_id, duration=None):
        if duration is None:
            duration = config.TIMER_DURATION
        start_time = datetime.now()
        expiration_time = start_time + timedelta(seconds=duration)

        # Save timer to the database
        execute_db_query('REPLACE INTO timers (discord_user_id, role_id, expiration_time, start_time) VALUES (?, ?, ?, ?)',
                         (user_id, role_id, expiration_time.isoformat(), start_time.isoformat()))

        logger.debug(f"Started a timer for user {user_id}, role {role_id}, to expire at {expiration_time.isoformat()}")

    def cancel_timer(self, user_id):
        execute_db_query('DELETE FROM timers WHERE discord_user_id = ?', (user_id,))
        logger.debug(f"Cancelled timer for user {user_id}")

    def load_timers(self):
        conn = sqlite3.connect('timers.db')
        c = conn.cursor()
        c.execute('SELECT discord_user_id, role_id, expiration_time FROM timers')
        rows = c.fetchall()
        conn.close()
        return rows

    def get_timer_info(self, user_id):
        conn = sqlite3.connect('timers.db')
        c = conn.cursor()
        c.execute('SELECT start_time FROM timers WHERE discord_user_id = ?', (user_id,))
        row = c.fetchone()
        conn.close()

        if row:
            return {
                "start_time": row[0]  # Return the start time directly
            }
        return None
