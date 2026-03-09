# Whitelister Assistant

Automated role management based on user activity. Integrates with MongoDB and SQL to track seeding points and hours played.

## Features
- Automatic Discord role assignment/removal.
- Seeding point tracking via Whitelister MongoDB.
- Activity tracking via SquadJS SQL data.
- SQLite-backed timer system for role expiration.

## Setup

### Environment Configuration
Copy `.env.example` to `.env` and configure:
- MongoDB connection (Whitelister).
- MySQL connection (SquadJS).
- Discord IDs (Guild, Roles).
- Thresholds (Hours, Points).

### Docker Deployment
```bash
docker compose up -d
```

### Manual Installation
```bash
pip install -r requirements.txt
python main.py
```

## Internal Architecture
- `database/`: Persistence layer (Mongo/SQL).
- `role_manager/`: Discord role logic.
- `utils/`: Core utilities and SQLite timer init.
- `main.py`: Entry point.

## Verification
Execute `scripts/verify.sh` for local integration testing.
