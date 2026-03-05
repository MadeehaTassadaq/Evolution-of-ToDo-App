#!/bin/bash
# ============================================
# KUBERNETES DEPLOYMENT SCRIPT
# ============================================
# Deploys the ToDo App with ChatKit to DigitalOcean Kubernetes
#
# Prerequisites:
# - kubectl configured with DOKS cluster
# - docker build and push completed
# - Secrets configured in 04-secrets.yaml
#
# Usage:
#   ./deploy-guide.sh          # Interactive mode
#   ./deploy-guide.sh auto     # Automated mode
#   ./deploy-guide.sh delete   # Delete everything

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="todo-app"
REGISTRY="todo-app"  # Change to your registry name
BACKEND_IMAGE="${REGISTRY}/todo-backend:latest"
FRONTEND_IMAGE="${REGISTRY}/todo-frontend:latest"

# ============================================
# UTILITY FUNCTIONS
# ============================================

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# ============================================
# PREREQUISITE CHECKS
# ============================================

check_prerequisites() {
    print_header "Checking Prerequisites"

    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl not found. Install from https://kubernetes.io/docs/tasks/tools/"
        exit 1
    fi
    print_success "kubectl is installed"

    # Check docker
    if ! command -v docker &> /dev/null; then
        print_error "docker not found. Install from https://docs.docker.com/get-docker/"
        exit 1
    fi
    print_success "docker is installed"

    # Check cluster connection
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Cannot connect to Kubernetes cluster. Check kubectl config"
        exit 1
    fi
    print_success "Connected to Kubernetes cluster"

    # Check if metrics server is installed (required for HPA)
    if ! kubectl get apiservice v1beta1.metrics.k8s.io &> /dev/null; then
        print_warning "Metrics Server not installed. HPA will not work."
        echo "  Install with: kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml"
    else
        print_success "Metrics Server is installed"
    fi

    echo ""
}

# ============================================
# STEP 1: BUILD DOCKER IMAGES
# ============================================

build_images() {
    print_header "Step 1: Building Docker Images"

    # Build backend
    print_warning "Building backend image..."
    cd "$(dirname "$0")/../phase_2_web_App/backend"
    docker build -t ${BACKEND_IMAGE} .
    print_success "Backend image built: ${BACKEND_IMAGE}"
    cd - > /dev/null

    # Build frontend
    print_warning "Building frontend image..."
    cd "$(dirname "$0")/../phase_2_web_App/frontend"
    docker build -t ${FRONTEND_IMAGE} .
    print_success "Frontend image built: ${FRONTEND_IMAGE}"
    cd - > /dev/null

    echo ""
}

# ============================================
# STEP 2: PUSH IMAGES TO REGISTRY
# ============================================

push_images() {
    print_header "Step 2: Pushing Images to Registry"

    print_warning "Pushing backend image..."
    docker push ${BACKEND_IMAGE}
    print_success "Backend image pushed"

    print_warning "Pushing frontend image..."
    docker push ${FRONTEND_IMAGE}
    print_success "Frontend image pushed"

    echo ""
}

# ============================================
# STEP 3: CREATE SECRETS
# ============================================

create_secrets() {
    print_header "Step 3: Creating Kubernetes Secrets"

    # Check if secrets file exists
    if [ ! -f "$(dirname "$0")/manifests/04-secrets.yaml" ]; then
        print_error "Secrets file not found at k8s/manifests/04-secrets.yaml"
        exit 1
    fi

    print_warning "Creating secrets from environment variables..."
    print_warning "Make sure these are set in your environment:"
    echo "  - DATABASE_URL"
    echo "  - OPENAI_API_KEY"
    echo "  - BETTER_AUTH_SECRET"
    echo "  - OPENAI_CHATKIT_DOMAIN_KEY"
    echo ""

    read -p "Have you set these environment variables? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Please set environment variables and run again"
        exit 1
    fi

    # Create secret safely
    kubectl create secret generic todo-secrets \
        -n ${NAMESPACE} \
        --from-literal=database-url="${DATABASE_URL}" \
        --from-literal=openai-api-key="${OPENAI_API_KEY}" \
        --from-literal=better-auth-secret="${BETTER_AUTH_SECRET}" \
        --from-literal=openai-chatkit-domain-key="${OPENAI_CHATKIT_DOMAIN_KEY}" \
        --dry-run=client -o yaml | kubectl apply -f -

    print_success "Secrets created"
    echo ""
}

# ============================================
# STEP 4: APPLY MANIFESTS
# ============================================

apply_manifests() {
    print_header "Step 4: Applying Kubernetes Manifests"

    local manifests_dir="$(dirname "$0")/manifests"

    # Apply in order
    print_warning "Applying namespace..."
    kubectl apply -f ${manifests_dir}/01-namespace.yaml
    print_success "Namespace created"

    print_warning "Applying configmap..."
    kubectl apply -f ${manifests_dir}/02-configmap.yaml
    print_success "ConfigMap created"

    print_warning "Applying backend deployment..."
    kubectl apply -f ${manifests_dir}/05-backend-deployment.yaml
    print_success "Backend deployment created"

    print_warning "Applying backend service..."
    kubectl apply -f ${manifests_dir}/06-backend-service.yaml
    print_success "Backend service created"

    print_warning "Applying frontend deployment..."
    kubectl apply -f ${manifests_dir}/07-frontend-deployment.yaml
    print_success "Frontend deployment created"

    print_warning "Applying frontend service..."
    kubectl apply -f ${manifests_dir}/08-frontend-service.yaml
    print_success "Frontend service created"

    print_warning "Applying HPA..."
    kubectl apply -f ${manifests_dir}/09-hpa.yaml
    print_success "HPA created"

    echo ""
}

# ============================================
# STEP 5: WAIT FOR DEPLOYMENT
# ============================================

wait_for_deployment() {
    print_header "Step 5: Waiting for Deployment"

    print_warning "Waiting for backend pods to be ready..."
    kubectl wait --for=condition=ready pod -l app=todo-backend -n ${NAMESPACE} --timeout=300s
    print_success "Backend pods are ready"

    print_warning "Waiting for frontend pods to be ready..."
    kubectl wait --for=condition=ready pod -l app=todo-frontend -n ${NAMESPACE} --timeout=300s
    print_success "Frontend pods are ready"

    echo ""
}

# ============================================
# STEP 6: SHOW STATUS
# ============================================

show_status() {
    print_header "Deployment Status"

    echo -e "${BLUE}Pods:${NC}"
    kubectl get pods -n ${NAMESPACE}

    echo ""
    echo -e "${BLUE}Services:${NC}"
    kubectl get services -n ${NAMESPACE}

    echo ""
    echo -e "${BLUE}HPA:${NC}"
    kubectl get hpa -n ${NAMESPACE}

    echo ""
    echo -e "${BLUE}Ingress:${NC}"
    kubectl get ingress -n ${NAMESPACE} 2>/dev/null || echo "No ingress configured"

    echo ""
    echo -e "${BLUE}External Access:${NC}"
    local external_ip=$(kubectl get service frontend-service -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    if [ -n "$external_ip" ]; then
        print_success "Application available at: http://${external_ip}"
    else
        print_warning "Waiting for external IP to be assigned..."
        print_warning "Run 'kubectl get services -n ${NAMESPACE}' to check"
    fi

    echo ""
}

# ============================================
# DELETE EVERYTHING
# ============================================

delete_all() {
    print_header "Deleting All Resources"

    read -p "Are you sure you want to delete all resources? (yes/no) " -r
    echo
    if [[ ! $REPLY == "yes" ]]; then
        print_warning "Deletion cancelled"
        exit 0
    fi

    print_warning "Deleting namespace and all resources..."
    kubectl delete namespace ${NAMESPACE}
    print_success "All resources deleted"
}

# ============================================
# MAIN FUNCTION
# ============================================

main() {
    print_header "ToDo App Kubernetes Deployment"
    echo ""

    case "${1:-}" in
        delete)
            delete_all
            ;;
        auto)
            check_prerequisites
            build_images
            push_images
            create_secrets
            apply_manifests
            wait_for_deployment
            show_status
            ;;
        *)
            check_prerequisites

            read -p "Build Docker images? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                build_images
            fi

            read -p "Push images to registry? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                push_images
            fi

            create_secrets
            apply_manifests
            wait_for_deployment
            show_status
            ;;
    esac

    print_success "Deployment complete!"
}

# Run main function with all arguments
main "$@"
