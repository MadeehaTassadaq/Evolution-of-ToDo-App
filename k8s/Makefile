# ============================================
# MAKEFILE FOR KUBERNETES DEPLOYMENT
# ============================================
# Convenient commands for managing the ToDo app on DOKS

.PHONY: help build push deploy delete status logs shell test all

# Configuration
NAMESPACE := todo-app
REGISTRY := todo-app
BACKEND_IMAGE := $(REGISTRY)/todo-backend:latest
FRONTEND_IMAGE := $(REGISTRY)/todo-frontend:latest
MANIFESTS_DIR := manifests

# Default target
help:
	@echo "ToDo App Kubernetes Deployment - Available Commands:"
	@echo ""
	@echo "  make build         - Build Docker images"
	@echo "  make push          - Push images to registry"
	@echo "  make deploy        - Deploy to Kubernetes"
	@echo "  make delete        - Delete all resources"
	@echo "  make status        - Show deployment status"
	@echo "  make logs          - Show logs from all pods"
	@echo "  make shell         - Open shell in backend pod"
	@echo "  make test          - Run health checks"
	@echo "  make all           - Build, push, and deploy"
	@echo ""
	@echo "Advanced Commands:"
	@echo "  make status-ns     - Show all resources in namespace"
	@echo "  make logs-backend  - Show backend logs"
	@echo "  make logs-frontend - Show frontend logs"
	@echo "  make restart       - Restart all pods"
	@echo "  make scale-up      - Scale up to 3 replicas"
	@echo "  make scale-down    - Scale down to 2 replicas"

# Build Docker images
build:
	@echo "Building Docker images..."
	cd ../phase_2_web_App/backend && docker build -t $(BACKEND_IMAGE) .
	cd ../phase_2_web_App/frontend && docker build -t $(FRONTEND_IMAGE) .
	@echo "✓ Build complete"

# Push images to registry
push:
	@echo "Pushing images to registry..."
	docker push $(BACKEND_IMAGE)
	docker push $(FRONTEND_IMAGE)
	@echo "✓ Push complete"

# Deploy to Kubernetes
deploy: deploy-base
	@echo "Waiting for deployment..."
	@kubectl wait --for=condition=ready pod -l app=todo-backend -n $(NAMESPACE) --timeout=300s
	@kubectl wait --for=condition=ready pod -l app=todo-frontend -n $(NAMESPACE) --timeout=300s
	@echo "✓ Deployment complete"
	@$(MAKE) status

# Deploy manifests (no wait)
deploy-base:
	@echo "Applying Kubernetes manifests..."
	kubectl apply -f $(MANIFESTS_DIR)/01-namespace.yaml
	kubectl apply -f $(MANIFESTS_DIR)/02-configmap.yaml
	kubectl apply -f $(MANIFESTS_DIR)/04-secrets.yaml
	kubectl apply -f $(MANIFESTS_DIR)/05-backend-deployment.yaml
	kubectl apply -f $(MANIFESTS_DIR)/06-backend-service.yaml
	kubectl apply -f $(MANIFESTS_DIR)/07-frontend-deployment.yaml
	kubectl apply -f $(MANIFESTS_DIR)/08-frontend-service.yaml
	kubectl apply -f $(MANIFESTS_DIR)/09-hpa.yaml
	@echo "✓ Manifests applied"

# Delete all resources
delete:
	@echo "Deleting namespace $(NAMESPACE)..."
	kubectl delete namespace $(NAMESPACE)
	@echo "✓ Delete complete"

# Show deployment status
status:
	@echo "=================================="
	@echo "Pods:"
	@kubectl get pods -n $(NAMESPACE)
	@echo ""
	@echo "=================================="
	@echo "Services:"
	@kubectl get services -n $(NAMESPACE)
	@echo ""
	@echo "=================================="
	@echo "HPA:"
	@kubectl get hpa -n $(NAMESPACE)
	@echo ""
	@echo "=================================="
	@echo "External IP:"
	@kubectl get service frontend-service -n $(NAMESPACE) -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# Show all resources in namespace
status-ns:
	kubectl get all -n $(NAMESPACE)

# Show logs from all pods
logs:
	@echo "Backend logs:"
	@kubectl logs -l app=todo-backend -n $(NAMESPACE) --tail=50 -f
	@echo ""
	@echo "Frontend logs:"
	@kubectl logs -l app=todo-frontend -n $(NAMESPACE) --tail=50 -f

# Show backend logs
logs-backend:
	kubectl logs -l app=todo-backend -n $(NAMESPACE) --tail=100 -f

# Show frontend logs
logs-frontend:
	kubectl logs -l app=todo-frontend -n $(NAMESPACE) --tail=100 -f

# Open shell in backend pod
shell:
	@kubectl exec -it -n $(NAMESPACE) $$(kubectl get pod -n $(NAMESPACE) -l app=todo-backend -o jsonpath='{.items[0].metadata.name}') -- /bin/sh

# Open shell in frontend pod
shell-frontend:
	@kubectl exec -it -n $(NAMESPACE) $$(kubectl get pod -n $(NAMESPACE) -l app=todo-frontend -o jsonpath='{.items[0].metadata.name}') -- /bin/sh

# Run health checks
test:
	@echo "Testing backend health..."
	@kubectl exec -n $(NAMESPACE) $$(kubectl get pod -n $(NAMESPACE) -l app=todo-backend -o jsonpath='{.items[0].metadata.name}') -- wget -q -O- http://localhost:8000/health
	@echo ""
	@echo "Testing frontend health..."
	@kubectl exec -n $(NAMESPACE) $$(kubectl get pod -n $(NAMESPACE) -l app=todo-frontend -o jsonpath='{.items[0].metadata.name}') -- wget -q -O- http://localhost:3000/
	@echo "✓ Health checks passed"

# Restart all pods
restart:
	@echo "Restarting pods..."
	kubectl rollout restart deployment backend-deployment -n $(NAMESPACE)
	kubectl rollout restart deployment frontend-deployment -n $(NAMESPACE)
	@echo "✓ Restart initiated"

# Scale up
scale-up:
	kubectl scale deployment backend-deployment --replicas=3 -n $(NAMESPACE)
	kubectl scale deployment frontend-deployment --replicas=3 -n $(NAMESPACE)
	@echo "✓ Scaled up to 3 replicas"

# Scale down
scale-down:
	kubectl scale deployment backend-deployment --replicas=2 -n $(NAMESPACE)
	kubectl scale deployment frontend-deployment --replicas=2 -n $(NAMESPACE)
	@echo "✓ Scaled down to 2 replicas"

# Build, push, and deploy
all: build push deploy

# Install metrics server (required for HPA)
install-metrics-server:
	kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Install NGINX ingress controller
install-ingress:
	kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.4/deploy/static/provider/do/deploy.yaml

# Port forward to local
port-forward:
	@echo "Port forwarding frontend to http://localhost:3000"
	@kubectl port-forward -n $(NAMESPACE) service/frontend-service 3000:80

# Port forward backend
port-forward-backend:
	@echo "Port forwarding backend to http://localhost:8000"
	@kubectl port-forward -n $(NAMESPACE) service/backend-service 8000:8000
