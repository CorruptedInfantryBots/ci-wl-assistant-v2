#!/bin/bash

cd "$(dirname "$0")/.."
COMPOSE_FILE="docker-compose.local.yml"

case "$1" in
  build)
    docker compose -f $COMPOSE_FILE build
    ;;
  up)
    docker compose -f $COMPOSE_FILE up -d
    ;;
  down)
    docker compose -f $COMPOSE_FILE down
    ;;
  logs)
    docker compose -f $COMPOSE_FILE logs -f
    ;;
  *)
    echo "Usage: $0 {build|up|down|logs}"
    exit 1
    ;;
esac
