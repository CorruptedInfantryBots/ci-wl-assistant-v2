import mysql.connector
import logging
import config

logger = logging.getLogger(__name__)

def connect_to_sql():
    try:
        cnx = mysql.connector.connect(
            host=config.SQL_HOST,
            user=config.SQL_USERNAME,
            password=config.SQL_PASSWORD,
            database=config.SQL_DATABASE,
            port=config.SQL_PORT
        )
        logger.info('Connected successfully to SQL database')
        return cnx
    except mysql.connector.Error as err:
        logger.error(f'Error connecting to SQL database: {err}')
        raise err
