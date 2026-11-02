#!/usr/bin/env bash
set -euo pipefail

# Usage: source scripts/set-env.sh
export PROJECT_ID="${PROJECT_ID:-YOUR_PROJECT_ID}"
export PROJECT_NUMBER="${PROJECT_NUMBER:-YOUR_PROJECT_NUMBER}"
export REGION="${REGION:-us-central1}"
export BUCKET="${BUCKET:-YOUR_GLOBALLY_UNIQUE_BUCKET}"
export ALLOYDB_CLUSTER="${ALLOYDB_CLUSTER:-ecommerce-cluster}"
export ALLOYDB_INSTANCE="${ALLOYDB_INSTANCE:-ecommerce-cluster-primary}"
export ALLOYDB_DATABASE="${ALLOYDB_DATABASE:-postgres}"
export ALLOYDB_USER="${ALLOYDB_USER:-postgres}"

if [[ "$PROJECT_ID" == "YOUR_PROJECT_ID" ]]; then
  echo "Set PROJECT_ID before continuing." >&2
  return 1 2>/dev/null || exit 1
fi
