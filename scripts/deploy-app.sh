#!/usr/bin/env bash
set -euo pipefail

: "${PROJECT_ID:?Set PROJECT_ID}"
: "${REGION:=us-central1}"
: "${SERVICE:=polyglot-retail-catalog}"
: "${TAG:=latest}"
: "${REPOSITORY:=containers}"

IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE}:${TAG}"

echo "Building ${IMAGE}"
gcloud builds submit --tag "${IMAGE}" .

echo "Deploying ${SERVICE} to Cloud Run"
gcloud run deploy "${SERVICE}" \
  --image "${IMAGE}" \
  --region "${REGION}" \
  --service-account "${SERVICE_ACCOUNT:-${PROJECT_NUMBER}-compute@developer.gserviceaccount.com}" \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT_ID},REGION=${REGION},DEMO_MODE=false" \
  --set-secrets "ALLOYDB_DSN=alloydb-dsn:latest,MONGODB_URI=mongodb-uri:latest" \
  --allow-unauthenticated \
  --cpu 1 \
  --memory 512Mi \
  --min-instances 0 \
  --max-instances 5 \
  --port 8080

echo "Service URL:"
gcloud run services describe "${SERVICE}" --region "${REGION}" --format='value(status.url)'
