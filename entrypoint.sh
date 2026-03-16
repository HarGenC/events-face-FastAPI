#!/bin/sh
set -e

until pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USERNAME
do
  sleep 2
done

echo "Running migrations..."
uv run alembic upgrade head

echo "Starting app..."
exec uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT