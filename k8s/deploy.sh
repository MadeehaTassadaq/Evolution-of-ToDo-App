#!/bin/bash

# Kubernetes Deployment Script for ToDo App
# This script handles the complete deployment workflow

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/home/madeeha/Documents/ToDoApp/Evolution-of-ToDo-App"
BACKEND_DIR="$PROJECT_ROOT/phase_2_web_App/backend"
FRONTEND_DIR="$PROJECT_ROOT/phase_2_web_App/frontend"
K8S_DIR="$PROJECT_ROOT/k8s"
CLUSTER_NAME="${CLUSTER_NAME:-kind}"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  ToDo App - Kubernetes Deployment Script${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Function to print colored output
print_step() {
    echo -e "\n${GREEN}➜ $1${NC}"
}

print_warning() {
    echo -e "\n${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "\n${RED}✗ $1${NC}"
}

# Step 1: Check Kind cluster
print_step "Step 1: Checking Kind cluster..."

if ! command -v kind &> /dev/null; then
    print_error "Kind is not installed. Please install Kind first:"
    echo "  curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64"
    echo "  chmod +x ./kind"
    echo "  sudo mv ./kind /usr/local/bin/kind"
    exit 1
fi

if ! kind get clusters | grep -q "^$CLUSTER_NAME$"; then
    print_warning "Kind cluster '$CLUSTER_NAME' not found. Creating..."
    kind create cluster --name $CLUSTER_NAME
else
    echo -e "${GREEN}✓${NC} Kind cluster '$CLUSTER_NAME' is running"
fi

# Step 2: Build Docker images
print_step "Step 2: Building Docker images..."

echo "Building backend image..."
cd "$BACKEND_DIR"
docker build -t todo-backend:local .

echo "Building frontend image..."
cd "$FRONTEND_DIR"
docker build -t todo-frontend:local .

echo -e "${GREEN}✓${NC} Docker images built successfully"

# Step 3: Load images into Kind
print_step "Step 3: Loading images into Kind cluster..."

kind load docker-image todo-backend:local --name $CLUSTER_NAME
kind load docker-image todo-frontend:local --name $CLUSTER_NAME

echo -e "${GREEN}✓${NC} Images loaded into Kind cluster"

# Step 4: Update secrets (if needed)
print_step "Step 4: Checking secrets..."
print_warning "Make sure to update k8s/02-secret.yaml with your actual credentials:"
echo "  - DATABASE_URL"
echo "  - JWT_SECRET_KEY"
echo "  - OPENAI_API_KEY"

read -p "Have you updated the secrets? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Please update k8s/02-secret.yaml before continuing"
    exit 1
fi

# Step 5: Apply Kubernetes manifests
print_step "Step 5: Applying Kubernetes manifests..."

cd "$K8S_DIR"

kubectl apply -f 00-namespace.yaml
kubectl apply -f 01-configmap.yaml
kubectl apply -f 02-secret.yaml
kubectl apply -f 03-backend-deployment.yaml
kubectl apply -f 04-backend-service.yaml
kubectl apply -f 05-frontend-deployment.yaml
kubectl apply -f 06-frontend-service.yaml

echo -e "${GREEN}✓${NC} All Kubernetes manifests applied"

# Step 6: Wait for deployments
print_step "Step 6: Waiting for deployments to be ready..."

echo "Waiting for backend deployment..."
kubectl wait --for=condition=available --timeout=300s \
    deployment/backend-deployment -n todoApp

echo "Waiting for frontend deployment..."
kubectl wait --for=condition=available --timeout=300s \
    deployment/frontend-deployment -n todoApp

echo -e "${GREEN}✓${NC} All deployments are ready"

# Step 7: Display status
print_step "Step 7: Deployment status"

echo ""
echo -e "${BLUE}Namespace:${NC}"
kubectl get ns todoApp

echo ""
echo -e "${BLUE}Deployments:${NC}"
kubectl get deployments -n todoApp

echo ""
echo -e "${BLUE}Services:${NC}"
kubectl get svc -n todoApp

echo ""
echo -e "${BLUE}Pods:${NC}"
kubectl get pods -n todoApp

# Step 8: Access information
print_step "Step 8: Access Information"

echo ""
echo -e "${GREEN}Your ToDo app is deployed!${NC}"
echo ""
echo "Access the application:"
echo "  - NodePort: http://localhost:30080"
echo "  - Port-forward: kubectl port-forward -n todoApp svc/frontend-service 3000:3000"
echo "              then: http://localhost:3000"
echo ""
echo "Useful commands:"
echo "  - View logs: kubectl logs -n todoApp -l app=todo-backend -f"
echo "  - Get pods: kubectl get pods -n todoApp"
echo "  - Describe pod: kubectl describe pod <pod-name> -n todoApp"
echo "  - Exec into pod: kubectl exec -it <pod-name> -n todoApp -- sh"
echo ""
echo -e "${BLUE}================================================${NC}"
