# Infrastructure & Deployment

## Runtime Environment
- Python 3.11
- Docker 24.0+
- Docker Compose v2.0+

## Key Dependencies
- `pymongo`
- `mysql-connector-python`
- `python-dotenv`
- `requests`

## Data Persistence
- `timers.db`
- Volume: `timers_data` maps to `/app/data`

## Local Development
```bash
cp .env.example .env.local
docker compose -f docker-compose.local.yml up -d
```

## Verification
```bash
chmod +x scripts/verify.sh
./scripts/verify.sh
```

## CI/CD Pipeline
GitHub Actions workflow in `.github/workflows/verify.yml` executes `scripts/verify.sh` on PRs.

## Secret Schema
Required environment variables for production deployment:
- `MONGODB_USERNAME`, `MONGODB_PASSWORD`, `MONGODB_HOST`, `MONGODB_PORT`: Whitelister database.
- `SQL_HOST`, `SQL_PORT`, `SQL_USERNAME`, `SQL_PASSWORD`, `SQL_DATABASE`: SquadJS database.
- `API_URL`: SquadJS API endpoint.
- `GUILD_ID`, `ROLE_ID`, `SEED_ROLE_ID`, `ACTIVITY_ROLE_ID`: Discord identifiers.
- `TIMER_DURATION`: SQLite role duration (seconds).

## Data Extraction Blueprint
To migrate existing data from the OLD box:
1. **SQLite (`timers.db`):** Copy the database file to the persistent volume on the new host.
2. **MongoDB:** No extraction needed if the assistant connects to the centralized Whitelister DB.
3. **MySQL:** No extraction needed as the assistant queries the SquadJS DB directly.

## Production Topology (Coolify)
- Target: Hetzner Box
- Network: Internal Docker bridge
- Proxy: Traefik
