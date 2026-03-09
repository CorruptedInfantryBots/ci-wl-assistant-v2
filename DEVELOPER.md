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

## Production Topology (Coolify)
- Target: Hetzner Box
- Network: Internal Docker bridge
- Proxy: Traefik
