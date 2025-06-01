#!/bin/bash

# Deploy script for RAG Ingestion Cloud Function
# Usage: ./scripts/deploy.sh [environment]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT=${1:-"dev"}
FUNCTION_NAME="rag-ingestion-function"
RUNTIME="python311"
REGION="us-central1"
ENTRY_POINT="process_rag_upload"
TIMEOUT="540s"
MEMORY="512MB"
MAX_INSTANCES="10"

# Load environment-specific config
if [ "$ENVIRONMENT" == "prod" ]; then
    ENV_FILE=".env.yaml.prod"
    BUCKET_NAME="mas-rag-documents-prod"
    SERVICE_ACCOUNT="rag-function-sa-prod"
else
    ENV_FILE=".env.yaml.local"
    BUCKET_NAME="mas-rag-documents-dev"
    SERVICE_ACCOUNT="rag-function-sa-dev"
fi

echo -e "${YELLOW}Deploying RAG Ingestion Function to ${ENVIRONMENT} environment${NC}"

# Check if env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}Error: Environment file $ENV_FILE not found${NC}"
    echo "Please create $ENV_FILE from .env.yaml template"
    exit 1
fi

# Get project ID from env file
PROJECT_ID=$(grep "GCP_PROJECT:" "$ENV_FILE" | cut -d'"' -f2)

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: GCP_PROJECT not found in $ENV_FILE${NC}"
    exit 1
fi

echo "Project ID: $PROJECT_ID"
echo "Bucket: $BUCKET_NAME"
echo "Service Account: $SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com"

# Confirm deployment
read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Deployment cancelled${NC}"
    exit 0
fi

# Deploy function
echo -e "${GREEN}Deploying Cloud Function...${NC}"

gcloud functions deploy "$FUNCTION_NAME-$ENVIRONMENT" \
  --gen2 \
  --runtime="$RUNTIME" \
  --region="$REGION" \
  --source=. \
  --entry-point="$ENTRY_POINT" \
  --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
  --trigger-event-filters="bucket=$BUCKET_NAME" \
  --env-vars-file="$ENV_FILE" \
  --service-account="$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com" \
  --timeout="$TIMEOUT" \
  --memory="$MEMORY" \
  --max-instances="$MAX_INSTANCES" \
  --project="$PROJECT_ID"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Function deployed successfully!${NC}"
    echo
    echo "Function URL: https://console.cloud.google.com/functions/details/$REGION/$FUNCTION_NAME-$ENVIRONMENT?project=$PROJECT_ID"
    echo
    echo "To test the function, upload a file to:"
    echo "  gsutil cp test.pdf gs://$BUCKET_NAME/"
else
    echo -e "${RED}✗ Function deployment failed${NC}"
    exit 1
fi