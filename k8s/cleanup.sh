#!/bin/bash

# Cleanup script for Kubernetes deployment

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}⚠ This will delete all resources in the todoApp namespace${NC}"
read -p "Are you sure? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}Deleting all resources in todoApp namespace...${NC}"
    kubectl delete all --all -n todoApp

    echo -e "${GREEN}Deleting namespace...${NC}"
    kubectl delete namespace todoApp

    echo -e "${GREEN}✓ Cleanup complete${NC}"
else
    echo "Cleanup cancelled"
fi
