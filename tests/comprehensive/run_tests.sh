#!/bin/bash

# Script to run comprehensive tests for all MAS agents and tools
# This ensures every tool in every agent is working correctly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}MAS Comprehensive Agent Testing${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo -e "${RED}Error: Virtual environment not found at $PROJECT_ROOT/venv${NC}"
    echo "Please create and activate the virtual environment first"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source "$PROJECT_ROOT/venv/bin/activate"

# Check environment variables
echo -e "${YELLOW}Checking environment configuration...${NC}"
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please create .env file with required configuration"
    exit 1
fi

# Export environment variables
export $(cat "$PROJECT_ROOT/.env" | grep -v '^#' | xargs)

# Run the comprehensive test
echo -e "${GREEN}Running comprehensive tests...${NC}"
echo

cd "$PROJECT_ROOT"
python3 tests/comprehensive/test_all_agents_tools.py

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ All tests completed successfully!${NC}"
else
    echo -e "\n${RED}❌ Some tests failed. Check the report for details.${NC}"
    exit 1
fi