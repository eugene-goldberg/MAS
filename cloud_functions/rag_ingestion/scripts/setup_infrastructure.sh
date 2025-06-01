#!/bin/bash

# Setup infrastructure for RAG Ingestion Cloud Function
# This script creates necessary GCP resources

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-"dev"}

if [ "$ENVIRONMENT" == "prod" ]; then
    BUCKET_NAME="mas-rag-documents-prod"
    SERVICE_ACCOUNT_NAME="rag-function-sa-prod"
else
    BUCKET_NAME="mas-rag-documents-dev"
    SERVICE_ACCOUNT_NAME="rag-function-sa-dev"
fi

# Get project info
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

echo -e "${YELLOW}Setting up infrastructure for $ENVIRONMENT environment${NC}"
echo "Project ID: $PROJECT_ID"
echo "Project Number: $PROJECT_NUMBER"

# 1. Create Cloud Storage bucket
echo -e "\n${GREEN}1. Creating Cloud Storage bucket...${NC}"
if gsutil ls -b gs://$BUCKET_NAME &>/dev/null; then
    echo "  Bucket $BUCKET_NAME already exists"
else
    gsutil mb -p $PROJECT_ID -c STANDARD -l us-central1 gs://$BUCKET_NAME/
    echo "  ✓ Created bucket: gs://$BUCKET_NAME"
fi

# Create folder structure
echo "  Creating folder structure..."
echo "" | gsutil cp - gs://$BUCKET_NAME/processed/placeholder.txt
echo "" | gsutil cp - gs://$BUCKET_NAME/failed/placeholder.txt
echo "  ✓ Created folders: processed/, failed/"

# 2. Create Service Account
echo -e "\n${GREEN}2. Creating Service Account...${NC}"
if gcloud iam service-accounts describe $SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com &>/dev/null; then
    echo "  Service account already exists"
else
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
        --display-name="RAG Ingestion Function Service Account ($ENVIRONMENT)" \
        --project=$PROJECT_ID
    echo "  ✓ Created service account: $SERVICE_ACCOUNT_NAME"
fi

# 3. Grant IAM permissions
echo -e "\n${GREEN}3. Granting IAM permissions...${NC}"

# Storage permissions
echo "  Granting storage permissions..."
gsutil iam ch serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com:objectViewer gs://$BUCKET_NAME
gsutil iam ch serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com:objectCreator gs://$BUCKET_NAME
gsutil iam ch serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com:legacyBucketWriter gs://$BUCKET_NAME

# Vertex AI permissions
echo "  Granting Vertex AI permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user" \
    --quiet

# Logging permissions
echo "  Granting logging permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/logging.logWriter" \
    --quiet

# 4. Enable required APIs
echo -e "\n${GREEN}4. Enabling required APIs...${NC}"
gcloud services enable cloudfunctions.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    run.googleapis.com \
    eventarc.googleapis.com \
    aiplatform.googleapis.com \
    storage.googleapis.com \
    --project=$PROJECT_ID

echo "  ✓ APIs enabled"

# 5. Create .env.yaml.local from template
echo -e "\n${GREEN}5. Creating environment configuration...${NC}"
if [ ! -f ".env.yaml.local" ]; then
    cp .env.yaml .env.yaml.local
    sed -i.bak "s/your-project-id/$PROJECT_ID/g" .env.yaml.local
    rm .env.yaml.local.bak
    echo "  ✓ Created .env.yaml.local"
    echo -e "  ${YELLOW}Please review and update .env.yaml.local with your settings${NC}"
else
    echo "  .env.yaml.local already exists"
fi

# 6. Grant Eventarc permissions
echo -e "\n${GREEN}6. Setting up Eventarc permissions...${NC}"
# Grant the pubsub.publisher role to the Cloud Storage service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:service-$PROJECT_NUMBER@gs-project-accounts.iam.gserviceaccount.com" \
    --role="roles/pubsub.publisher" \
    --quiet

echo "  ✓ Eventarc permissions configured"

# Summary
echo -e "\n${GREEN}✓ Infrastructure setup complete!${NC}"
echo
echo "Resources created:"
echo "  - Bucket: gs://$BUCKET_NAME"
echo "  - Service Account: $SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"
echo "  - Folder structure: processed/, failed/"
echo
echo "Next steps:"
echo "  1. Review and update .env.yaml.local"
echo "  2. Run ./scripts/deploy.sh to deploy the function"
echo "  3. Test by uploading a file to gs://$BUCKET_NAME/"