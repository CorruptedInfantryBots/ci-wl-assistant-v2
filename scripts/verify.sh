#!/bin/bash
set -e

cd "$(dirname "$0")/.."

cp .env.example .env.local
sed -i 's/SQL_PASSWORD=.*/SQL_PASSWORD=password/' .env.local
sed -i 's/MONGODB_PASSWORD=.*/MONGODB_PASSWORD=toor/' .env.local
sed -i 's/GUILD_ID=.*/GUILD_ID=1234/' .env.local
sed -i 's/ROLE_ID=.*/ROLE_ID=1234/' .env.local
sed -i 's/SEED_ROLE_ID=.*/SEED_ROLE_ID=1234/' .env.local
sed -i 's/ACTIVITY_ROLE_ID=.*/ACTIVITY_ROLE_ID=1234/' .env.local

docker compose -f docker-compose.local.yml up -d --build

MAX_RETRIES=3
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  sleep 5
  if docker compose -f docker-compose.local.yml logs assistant | grep -q "Processed 1 users"; then
    echo "Verification Successful: Service processed dummy data."
    docker compose -f docker-compose.local.yml down
    exit 0
  fi
  RETRY_COUNT=$((RETRY_COUNT+1))
done

echo "Verification Failed: Service logs did not show expected dummy data processing."
docker compose -f docker-compose.local.yml logs
docker compose -f docker-compose.local.yml down
exit 1
