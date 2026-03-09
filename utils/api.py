import logging
import requests
from ratelimiter import RateLimiter
from threading import Lock
import config

logger = logging.getLogger(__name__)

class APIClient:
    """
    Abstract base class for API clients.
    """
    def add_role(self, guild_id, user_id, role_id):
        raise NotImplementedError

    def remove_role(self, guild_id, user_id, role_id, timestamp):
        raise NotImplementedError

class CustomAPIClient(APIClient):
    """
    Concrete implementation of APIClient for the custom API.
    """
    def __init__(self, api_url, rate_limit=4, period=1):
        self.api_url = api_url
        self.api_lock = Lock()
        self.limiter = RateLimiter(max_calls=rate_limit, period=period)  # e.g., 4 requests per second

    def add_role(self, guild_id, user_id, role_id):
        with self.api_lock:
            with self.limiter:
                logger.debug(f"Assigning role {role_id} to user {user_id}")
                data = {
                    "guildId": guild_id,
                    "userId": user_id,
                    "roleId": role_id
                }
                try:
                    response = requests.post(f"{self.api_url}/add-role", json=data)
                    if response.status_code == 200:
                        logger.debug(f"Role {role_id} added to user {user_id} via API call.")
                    else:
                        logger.error(f"Failed to add role to user {user_id}: {response.status_code} {response.text}")
                except Exception as e:
                    logger.error(f"Error adding role to user {user_id}: {e}")

    def remove_role(self, guild_id, user_id, role_id, timestamp=None):
        with self.api_lock:
            with self.limiter:
                logger.debug(f"Removing role {role_id} from user {user_id}")
                data = {
                    "guildId": guild_id,
                    "userId": user_id,
                    "roleId": role_id,
                }
                if timestamp is not None:
                    data["timestamp"] = timestamp
                    logger.debug(f"Including timestamp: {timestamp}")
                try:
                    response = requests.post(f"{self.api_url}/remove-role", json=data)
                    if response.status_code == 200:
                        logger.debug(f"Role {role_id} removed from user {user_id} via API call.")
                    else:
                        logger.error(f"Failed to remove role from user {user_id}: {response.status_code} {response.text}")
                except Exception as e:
                    logger.error(f"Error removing role from user {user_id}: {e}")

# Factory function to instantiate the appropriate API client
def get_api_client():
    """
    Factory function to return an instance of APIClient.
    Modify this function to return different API clients as needed.
    """
    return CustomAPIClient(api_url=config.API_URL)
