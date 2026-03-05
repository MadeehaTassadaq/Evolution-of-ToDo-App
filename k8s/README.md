# Kubernetes Deployment Guide

# ToDo App with ChatKit - DigitalOcean Kubernetes Deployment

This guide covers deploying the ToDo application with OpenAI ChatKit integration to DigitalOcean Kubernetes (DOKS).

## Table of Contents

- [Prerequisites](#prerequisites)
- [Architecture Overview](#architecture-overview)
- [Quick Start](#quick-start)
- [Detailed Deployment Steps](#detailed-deployment-steps)
- [Configuration](#configuration)
- [Monitoring and Scaling](#monitoring-and-scaling)
- [Troubleshooting](#troubleshooting)
- [Cost Optimization](#cost-optimization)

---

## Prerequisites

### Required Tools

| Tool | Purpose | Installation |
|------|---------|--------------|
| **kubectl** | Kubernetes CLI | [Install Guide](https://kubernetes.io/docs/tasks/tools/) |
| **docker** | Build images | [Install Guide](https://docs.docker.com/get-docker/) |
| **doctl** | DigitalOcean CLI (optional) | [Install Guide](https://docs.digitalocean.com/reference/doctl/) |

### Required Accounts

- DigitalOcean account with active subscription
- DigitalOcean Container Registry (optional, but recommended)

### Cluster Requirements

- DigitalOcean Kubernetes cluster (any size)
- Minimum: 1 node (basic-$10/month for testing)
- Recommended: 2-3 nodes for production
- Kubernetes version: 1.24+

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    DigitalOcean Load Balancer                   │
│                      (frontend-service)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      NGINX Ingress (Optional)                   │
│                   Routes + SSL/TLS Termination                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│  Frontend Deployment     │    │  Backend Deployment      │
│  - Next.js 16            │    │  - FastAPI                │
│  - ChatKit Widget        │    │  - ChatKit Python SDK     │
│  - 2-5 replicas (HPA)    │    │  - 2-10 replicas (HPA)    │
└──────────────────────────┘    └──────────────────────────┘
                │                           │
                └───────────┬───────────────┘
                            ▼
                    ┌──────────────────┐
                    │  Neon PostgreSQL │
                    │  (External DB)   │
                    └──────────────────┘
```

### Kubernetes Resources

| Resource | Type | Replicas | Purpose |
|----------|------|----------|---------|
| **backend-deployment** | Deployment | 2 (scales to 10) | FastAPI + ChatKit |
| **frontend-deployment** | Deployment | 2 (scales to 5) | Next.js + ChatKit Widget |
| **backend-service** | ClusterIP | - | Internal backend access |
| **frontend-service** | LoadBalancer | - | External frontend access |
| **backend-hpa** | HPA | - | Auto-scale backend |
| **frontend-hpa** | HPA | - | Auto-scale frontend |
| **todo-ingress** | Ingress | - | Routing + SSL (optional) |

---

## Quick Start

### 1. Set Environment Variables

```bash
# Database (Neon PostgreSQL)
export DATABASE_URL="postgresql://neondb_owner:PASSWORD@ep-xxx.pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

# OpenAI API Key
export OPENAI_API_KEY="sk-proj-..."

# Better Auth Secret
export BETTER_AUTH_SECRET="your-secret-min-32-chars"

# ChatKit Domain Key
export OPENAI_CHATKIT_DOMAIN_KEY="domain_pk_..."
```

### 2. Connect to DOKS Cluster

```bash
# Via DigitalOcean dashboard: "Connect to Cluster" button
# Or manually:
kubectl config use-context do-<region>-<cluster-name>
```

### 3. Deploy

```bash
# Make deployment script executable
chmod +x deploy-guide.sh

# Run automated deployment
./deploy-guide.sh auto
```

### 4. Access Application

```bash
# Get external IP
kubectl get service frontend-service -n todo-app

# Or use make
make status
```

---

## Detailed Deployment Steps

### Step 1: Prepare DigitalOcean Container Registry

```bash
# Login to DO registry
doctl registry login

# Create registry (one-time)
doctl registry create todo-app

# Set registry variable
export REGISTRY="registry.digitalocean.com/todo-app"
```

### Step 2: Build Docker Images

```bash
# Build backend
cd phase_2_web_App/backend
docker build -t ${REGISTRY}/todo-backend:latest .
cd ../..

# Build frontend
cd phase_2_web_App/frontend
docker build -t ${REGISTRY}/todo-frontend:latest .
cd ../..
```

### Step 3: Push Images

```bash
docker push ${REGISTRY}/todo-backend:latest
docker push ${REGISTRY}/todo-frontend:latest
```

### Step 4: Create Kubernetes Secrets

```bash
kubectl create secret generic todo-secrets \
  -n todo-app \
  --from-literal=database-url="${DATABASE_URL}" \
  --from-literal=openai-api-key="${OPENAI_API_KEY}" \
  --from-literal=better-auth-secret="${BETTER_AUTH_SECRET}" \
  --from-literal=openai-chatkit-domain-key="${OPENAI_CHATKIT_DOMAIN_KEY}"
```

### Step 5: Apply Manifests

```bash
# Apply all manifests
kubectl apply -f k8s/manifests/

# Or apply individually
kubectl apply -f k8s/manifests/01-namespace.yaml
kubectl apply -f k8s/manifests/02-configmap.yaml
kubectl apply -f k8s/manifests/04-secrets.yaml
kubectl apply -f k8s/manifests/05-backend-deployment.yaml
kubectl apply -f k8s/manifests/06-backend-service.yaml
kubectl apply -f k8s/manifests/07-frontend-deployment.yaml
kubectl apply -f k8s/manifests/08-frontend-service.yaml
kubectl apply -f k8s/manifests/09-hpa.yaml
```

### Step 6: Verify Deployment

```bash
# Check pods
kubectl get pods -n todo-app

# Check services
kubectl get services -n todo-app

# Get external IP
kubectl get service frontend-service -n todo-app -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

---

## Configuration

### Image Registry

Update `05-backend-deployment.yaml` and `07-frontend-deployment.yaml`:

```yaml
# Change from:
image: todo-backend:latest

# To:
image: registry.digitalocean.com/todo-app/todo-backend:latest
```

### Resource Limits

Adjust in deployment manifests:

```yaml
resources:
  requests:
    memory: "256Mi"   # Increase for heavier workloads
    cpu: "250m"
  limits:
    memory: "512Mi"   # Adjust based on needs
    cpu: "500m"
```

### HPA Scaling

Edit `09-hpa.yaml`:

```yaml
spec:
  minReplicas: 2      # Minimum running pods
  maxReplicas: 10     # Maximum pods during traffic spikes
```

### Ingress and SSL

To enable HTTPS with a custom domain:

1. **Install NGINX Ingress Controller:**
   ```bash
   kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.4/deploy/static/provider/do/deploy.yaml
   ```

2. **Install cert-manager:**
   ```bash
   kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
   ```

3. **Create Let's Encrypt ClusterIssuer:**
   ```bash
   kubectl apply -f - <<EOF
   apiVersion: cert-manager.io/v1
   kind: ClusterIssuer
   metadata:
     name: letsencrypt-prod
   spec:
     acme:
       server: https://acme-v02.api.letsencrypt.org/directory
       email: your@email.com
       privateKeySecretRef:
         name: letsencrypt-prod
       solvers:
       - http01:
           ingress:
             class: nginx
   EOF
   ```

4. **Update `10-ingress.yaml`** with your domain and apply.

---

## Monitoring and Scaling

### View Logs

```bash
# All pods
make logs

# Backend only
make logs-backend

# Frontend only
make logs-frontend
```

### Scaling

```bash
# Manual scale up
make scale-up

# Manual scale down
make scale-down

# Check HPA status
kubectl get hpa -n todo-app -w
```

### Resource Usage

```bash
# Pod resource usage
kubectl top pods -n todo-app

# Node resource usage
kubectl top nodes
```

---

## Troubleshooting

### Pods Not Starting

```bash
# Describe pod for details
kubectl describe pod -n todo-app -l app=todo-backend

# Check pod logs
kubectl logs -n todo-app -l app=todo-backend --previous
```

### External IP Pending

The LoadBalancer takes 1-2 minutes to assign an IP:

```bash
# Watch for IP assignment
kubectl get service frontend-service -n todo-app -w
```

### SSE Streaming Not Working

Check Ingress configuration has:

```yaml
nginx.ingress.kubernetes.io/proxy-buffering: "off"
nginx.ingress.kubernetes.io/proxy-request-buffering: "off"
```

### Health Checks Failing

```bash
# Test health endpoint directly
kubectl exec -it -n todo-app <pod-name> -- wget -q -O- http://localhost:8000/health
```

---

## Cost Optimization

### Monthly Cost Estimate (DigitalOcean)

| Resource | Spec | Cost |
|----------|------|------|
| **Kubernetes Cluster** | 2 x basic-$10 nodes | $20/month |
| **Load Balancer** | 1 x LB | $10/month |
| **Container Registry** | Basic tier | $5/month |
| **Neon Database** | Serverless | ~$0-20/month |
| **Total** | | ~$35-55/month |

### Cost Reduction Tips

1. **Use Ingress instead of multiple LoadBalancers:**
   - One LB for all services via Ingress controller
   - Saves $10/month per additional service

2. **Scale HPA minimum to 1 for testing:**
   ```yaml
   minReplicas: 1  # For non-critical apps
   ```

3. **Use smaller nodes for development:**
   - basic-$10 instead of basic-$20

4. **Delete cluster when not in use:**
   ```bash
   make delete  # Removes all resources
   ```

---

## Useful Commands

```bash
# Make commands
make help        # Show all commands
make status      # Show deployment status
make logs        # Show all logs
make test        # Run health checks
make restart     # Restart pods

# kubectl commands
kubectl get all -n todo-app                    # All resources
kubectl top pods -n todo-app                    # Resource usage
kubectl exec -it <pod> -n todo-app -- /bin/sh   # Shell access
kubectl port-forward -n todo-app svc/frontend-service 3000:80  # Local access
```

---

## Next Steps

1. **Set up CI/CD** for automated deployments
2. **Configure monitoring** (Prometheus, Grafana)
3. **Set up alerts** (Discord, Slack, email)
4. **Enable SSL/TLS** with custom domain
5. **Configure backup** for database
6. **Set up staging environment**

---

## Support

- DigitalOcean Kubernetes Docs: https://docs.digitalocean.com/products/kubernetes/
- Kubernetes Docs: https://kubernetes.io/docs/
- Project Issues: https://github.com/your-repo/issues
