#!/bin/bash

# Test script for RAG Ingestion Cloud Function
# Tests both local and deployed versions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-"dev"}
TEST_FILE=${2:-"test_document.txt"}

if [ "$ENVIRONMENT" == "prod" ]; then
    BUCKET_NAME="mas-rag-documents-prod"
else
    BUCKET_NAME="mas-rag-documents-dev"
fi

echo -e "${YELLOW}Testing RAG Ingestion Function ($ENVIRONMENT)${NC}"

# 1. Create test file
echo -e "\n${GREEN}1. Creating test file...${NC}"
cat > "$TEST_FILE" << EOF
This is a test document for the RAG ingestion function.

Title: Test Document for Cloud Function
Date: $(date)

Content:
The RAG ingestion function should process this document and add it to the Vertex AI RAG corpus.
This test verifies that:
1. File upload triggers the function
2. Function processes the file correctly
3. File is moved to processed folder
4. Document is added to RAG corpus

Test data:
- Lorem ipsum dolor sit amet, consectetur adipiscing elit.
- Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
- Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.
EOF

echo "  ✓ Created test file: $TEST_FILE"

# 2. Upload test file
echo -e "\n${GREEN}2. Uploading test file to Cloud Storage...${NC}"
gsutil cp "$TEST_FILE" "gs://$BUCKET_NAME/"
echo "  ✓ Uploaded to: gs://$BUCKET_NAME/$TEST_FILE"

# 3. Wait for processing
echo -e "\n${GREEN}3. Waiting for function to process file...${NC}"
echo "  Waiting 30 seconds for processing..."
sleep 30

# 4. Check if file was processed
echo -e "\n${GREEN}4. Checking processing status...${NC}"

# Check processed folder
if gsutil ls "gs://$BUCKET_NAME/processed/$TEST_FILE" &>/dev/null; then
    echo -e "  ${GREEN}✓ File successfully processed!${NC}"
    echo "  File moved to: gs://$BUCKET_NAME/processed/$TEST_FILE"
    
    # Download and check metadata
    gsutil cp "gs://$BUCKET_NAME/processed/$TEST_FILE" "/tmp/processed_$TEST_FILE"
    echo "  ✓ Downloaded processed file for verification"
    
elif gsutil ls "gs://$BUCKET_NAME/failed/$TEST_FILE" &>/dev/null; then
    echo -e "  ${RED}✗ File processing failed!${NC}"
    echo "  File moved to: gs://$BUCKET_NAME/failed/$TEST_FILE"
    
    # Check error log
    if gsutil ls "gs://$BUCKET_NAME/failed/$TEST_FILE.error.json" &>/dev/null; then
        echo -e "\n  ${YELLOW}Error details:${NC}"
        gsutil cat "gs://$BUCKET_NAME/failed/$TEST_FILE.error.json" | jq '.'
    fi
    
else
    echo -e "  ${YELLOW}⚠ File not found in processed or failed folders${NC}"
    echo "  File might still be processing or function might not have triggered"
fi

# 5. Check function logs
echo -e "\n${GREEN}5. Checking function logs...${NC}"
FUNCTION_NAME="rag-ingestion-function-$ENVIRONMENT"
echo "  Fetching logs for: $FUNCTION_NAME"
echo

gcloud functions logs read "$FUNCTION_NAME" \
    --region=us-central1 \
    --limit=20 \
    --format="table(time, severity, text)" \
    --filter="text:$TEST_FILE OR text:process_rag_upload"

# 6. Cleanup
echo -e "\n${GREEN}6. Cleanup...${NC}"
rm -f "$TEST_FILE"
echo "  ✓ Removed local test file"

echo -e "\n${GREEN}Test complete!${NC}"