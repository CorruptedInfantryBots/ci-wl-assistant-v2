# Whitelister Assistant

## Overview

Whitelister Assistant automates role assignments in Discord based on user activity. It integrates with MongoDB and SQL databases to manage roles by tracking points and hours played, offering a streamlined solution for monitoring in-game activity and dynamically adding or removing roles on the Discord server. 

## Features
- Automatic role assignments/removals based on:
  - Seeding points from [Whitelister](https://github.com/fantinodavide/Squad_Whitelister).
  - Hours played tracked by [SquadJS](https://github.com/Team-Silver-Sphere/SquadJS) plugin ActivityTracker.

## Directory Structure

- `database/`: Manages database connections.
- `role_manager/`: Handles role operations.
- `utils/`: Utility functions.
- `main.py`: Application entry point.
- `config.py`: Configuration variables.

## Setup Instructions

### Prerequisites

- Python 3.x
- [Whitelister](https://github.com/fantinodavide/Squad_Whitelister) MongoDB database
- ActivityTracker plugin for [SquadJS](https://github.com/Team-Silver-Sphere/SquadJS)
- Discord Bot API access for role management

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/michalniko/Whitelister_Assistant.git
   cd Whitelister_Assistant
   ```

2. **Create a Virtual Environment**
   
   ```bash
   python -m venv env
   source env/bin/activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**

    Create a `.env` file in the root directory and configure it with your MongoDB, SQL, API, and Discord settings.

    **Example .env**
   ```bash
   # MongoDB
   MONGODB_USERNAME=username
   MONGODB_PASSWORD=password
   MONGODB_HOST=localhost
   MONGODB_PORT=12345

   # True if you want to work on cloned MongoDB instance
   # False to skip this part and use main MongoDb instance
   USE_DB_CLONE=False
   MONGODB_MAIN_DATA_PATH=/path/to/main/mongodb/data
   MONGODB_CLONE_DATA_PATH=/path/to/clone/mongodb/data
   MONGODB_CLONE_CONTAINER_NAME=mongodb_clone

   # Double check the paths to main and clone

   # SQL Database 
   SQL_HOST=localhost
   SQL_PORT=1234
   SQL_USERNAME=username
   SQL_PASSWORD=password
   SQL_DATABASE=database

   # API 
   API_URL=http://127.0.0.1:1234

   # Discord 
   GUILD_ID=123456789123456789
   ROLE_ID=123456789123456789
   SEED_ROLE_ID=123456789123456789
   ACTIVITY_ROLE_ID=123456789123456789

   # Number of weeks to consider for hours played
   HOURS_PLAYED_WEEKS=2
   HOURS_THRESHOLD=25  # Number of hours required in the past week

   # Lenghts of whitelist after dropping bellow seed point threshold
   TIMER_DURATION=500  # In seconds

   # Logging 
   LOG_FILE=app.log
   LOG_MAX_BYTES=1000000
   LOG_BACKUP_COUNT=5
    ```

   ## Usage

   Run the application with:
   ```bash
   python3 main.py
   ```
   
   ## Contributing

   Contributions are welcome.

   ## License
   
   This project is licensed under the [MIT License](LICENSE).
