#!/usr/bin/env bash
# Production deploy: run migrations, then roll the API pods (3 replicas, read replica for reports).
set -euo pipefail
psql "$DATABASE_URL" -f migrations/latest.sql
kubectl rollout restart deployment/shop-api
