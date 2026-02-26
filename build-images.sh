#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building Docker images for ToDo App...${NC}"

# Registry (use local by default, can override with DOCKER_REGISTRY env var)
REGISTRY=${DOCKER_REGISTRY:-localhost}
VERSION=${VERSION:-latest}

# Image names
PHASE2_BACKEND_IMAGE="${REGISTRY}/todo-phase2-backend:${VERSION}"
PHASE3_BACKEND_IMAGE="${REGISTRY}/todo-phase3-backend:${VERSION}"
FRONTEND_IMAGE="${REGISTRY}/todo-frontend:${VERSION}"

# Build Phase 2 Backend (Todo CRUD - Port 8000)
echo -e "${YELLOW}Building Phase 2 Backend (Todo CRUD)...${NC}"
cd phase_2_web_App/backend
docker build -t ${PHASE2_BACKEND_IMAGE} .
cd ../..

# Build Phase 3 Backend (AI Chatbot - Port 7860)
echo -e "${YELLOW}Building Phase 3 Backend (AI Chatbot)...${NC}"
cd phase_3_chatbot/backend
docker build -t ${PHASE3_BACKEND_IMAGE} .
cd ../..

# Build Frontend (Next.js - Port 3000)
echo -e "${YELLOW}Building Frontend...${NC}"
cd phase_2_web_App/frontend
docker build -t ${FRONTEND_IMAGE} .
cd ../..

echo -e "${GREEN}All images built successfully!${NC}"
echo ""
echo "Images:"
echo "  - Phase 2 Backend: ${PHASE2_BACKEND_IMAGE}"
echo "  - Phase 3 Backend: ${PHASE3_BACKEND_IMAGE}"
echo "  - Frontend:        ${FRONTEND_IMAGE}"
echo ""
echo "To run containers:"
echo "  docker run -p 8000:8000 --env-file .env ${PHASE2_BACKEND_IMAGE}"
echo "  docker run -p 7860:7860 --env-file .env ${PHASE3_BACKEND_IMAGE}"
echo "  docker run -p 3000:3000 --env-file .env.local ${FRONTEND_IMAGE}"
