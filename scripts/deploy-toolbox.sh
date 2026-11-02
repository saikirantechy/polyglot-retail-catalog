#!/usr/bin/env bash
set -euo pipefail

: "${PROJECT_ID:?Set PROJECT_ID}"
: "${PROJECT_NUMBER:?Set PROJECT_NUMBER}"
: "${REGION:=us-central1}"
: "${VERSION:=1.15.0}"

# This script assumes the Secret Manager secret 'tools' already exists
# and contains a validated, credential-safe tools.yaml configuration.
gcloud run deploy toolbox \
  --image "us-central1-docker.pkg.dev/database-toolbox/toolbox/toolbox:${VERSION}" \
  --region "${REGION}" \
  --service-account "${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --set-secrets "/app/tools.yaml=tools:latest" \
  --args="--config=/app/tools.yaml","--address=0.0.0.0","--port=8080","--ui","--enable-api" \
  --allow-unauthenticated
