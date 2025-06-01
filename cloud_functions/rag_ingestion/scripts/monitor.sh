#!/bin/bash

# Monitor script for RAG Ingestion Cloud Function
# Provides real-time monitoring and statistics

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-"dev"}
REFRESH_INTERVAL=${2:-30}

if [ "$ENVIRONMENT" == "prod" ]; then
    BUCKET_NAME="mas-rag-documents-prod"
    FUNCTION_NAME="rag-ingestion-function-prod"
else
    BUCKET_NAME="mas-rag-documents-dev"
    FUNCTION_NAME="rag-ingestion-function-dev"
fi

PROJECT_ID=$(gcloud config get-value project)

echo -e "${BLUE}RAG Ingestion Monitor - ${ENVIRONMENT} environment${NC}"
echo "Project: $PROJECT_ID"
echo "Bucket: $BUCKET_NAME"
echo "Function: $FUNCTION_NAME"
echo "Refresh: Every ${REFRESH_INTERVAL}s (Ctrl+C to exit)"
echo

# Function to get bucket stats
get_bucket_stats() {
    local pending=$(gsutil ls gs://$BUCKET_NAME/*.* 2>/dev/null | wc -l || echo "0")
    local processed=$(gsutil ls gs://$BUCKET_NAME/processed/ 2>/dev/null | wc -l || echo "0")
    local failed=$(gsutil ls gs://$BUCKET_NAME/failed/*.* 2>/dev/null | grep -v ".error.json" | wc -l || echo "0")
    
    echo -e "\n${GREEN}📊 Bucket Statistics${NC}"
    echo "├─ Pending: $pending files"
    echo "├─ Processed: $processed files"
    echo "└─ Failed: $failed files"
}

# Function to get recent logs
get_recent_logs() {
    echo -e "\n${YELLOW}📋 Recent Function Logs${NC}"
    gcloud functions logs read "$FUNCTION_NAME" \
        --region=us-central1 \
        --limit=5 \
        --format="table(time.date('%H:%M:%S'), severity, text)" \
        --filter="severity>=INFO" 2>/dev/null || echo "No recent logs"
}

# Function to get function metrics
get_function_metrics() {
    echo -e "\n${BLUE}📈 Function Metrics${NC}"
    
    # Get function details
    local details=$(gcloud functions describe "$FUNCTION_NAME" \
        --region=us-central1 \
        --format="value(state,updateTime)" 2>/dev/null || echo "UNKNOWN Unknown")
    
    local state=$(echo $details | cut -d' ' -f1)
    local update_time=$(echo $details | cut -d' ' -f2)
    
    echo "├─ State: $state"
    echo "└─ Last Updated: $update_time"
}

# Function to check recent errors
check_recent_errors() {
    echo -e "\n${RED}⚠️  Recent Errors${NC}"
    
    # Check for recent error files
    local error_files=$(gsutil ls gs://$BUCKET_NAME/failed/*.error.json 2>/dev/null | tail -3)
    
    if [ -z "$error_files" ]; then
        echo "No recent errors"
    else
        echo "$error_files" | while read error_file; do
            if [ ! -z "$error_file" ]; then
                echo -e "\n${YELLOW}Error file: $(basename $error_file)${NC}"
                gsutil cat "$error_file" 2>/dev/null | jq -r '"\(.timestamp): \(.error)" | .[0:100]' || echo "Could not read error"
            fi
        done
    fi
}

# Function to show processing rate
show_processing_rate() {
    echo -e "\n${GREEN}⚡ Processing Rate (last hour)${NC}"
    
    # Count logs with "Successfully processed" in the last hour
    local success_count=$(gcloud functions logs read "$FUNCTION_NAME" \
        --region=us-central1 \
        --limit=1000 \
        --format="value(text)" \
        --filter="text:'Successfully processed' AND timestamp>=\"$(date -u -d '1 hour ago' '+%Y-%m-%dT%H:%M:%S')\"" 2>/dev/null | wc -l || echo "0")
    
    echo "Files processed in last hour: $success_count"
}

# Main monitoring loop
while true; do
    clear
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}     RAG Ingestion Monitor - $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    
    get_bucket_stats
    get_function_metrics
    show_processing_rate
    get_recent_logs
    check_recent_errors
    
    echo -e "\n${YELLOW}Refreshing in ${REFRESH_INTERVAL} seconds... (Ctrl+C to exit)${NC}"
    sleep $REFRESH_INTERVAL
done