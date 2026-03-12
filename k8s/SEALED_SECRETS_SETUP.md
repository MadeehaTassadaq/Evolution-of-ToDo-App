# Sealed Secrets Setup Guide

## Overview

SealedSecrets allows you to encrypt Kubernetes Secrets so they're safe to commit to Git. Only your cluster can decrypt them.

**How it works:**
1. Install SealedSecrets controller on your cluster
2. Use `kubeseal` CLI to encrypt secrets with the controller's public key
3. Commit the encrypted `SealedSecret` to Git
4. Controller automatically decrypts and creates regular Secrets

---

## Prerequisites

- Kubernetes cluster running (Kind, Minikube, DOKS, etc.)
- `kubectl` configured and connected to your cluster
- `kubeseal` CLI tool installed

---

## Step 1: Install kubeseal CLI

### Option A: Download from releases (Recommended)

```bash
# Download kubeseal
wget https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/kubeseal-0.24.0-linux-amd64.tar.gz

# Extract
tar -xzf kubeseal-0.24.0-linux-amd64.tar.gz

# Install to /usr/local/bin
sudo install kubeseal /usr/local/bin/kubeseal

# Verify installation
kubeseal --version
```

### Option B: Use the downloaded file (Already in your project)

```bash
# Extract from the tarball in your project
cd /home/madeeha/Documents/ToDoApp/Evolution-of-ToDo-App
tar -xzf kubeseal-0.24.0-linux-amd64.tar.gz

# Install locally (no sudo needed)
mkdir -p ~/.local/bin
install kubeseal ~/.local/bin/kubeseal

# Add to PATH (add to ~/.bashrc for persistence)
export PATH=$PATH:$HOME/.local/bin
```

---

## Step 2: Install SealedSecrets Controller

Install the controller on your Kubernetes cluster:

```bash
kubectl apply -f k8s/sealed-secrets-controller.yaml
```

Wait for the controller to be ready:

```bash
kubectl wait --for=condition=available --timeout=60s \
  -n kube-system deployment/sealed-secrets-controller
```

Verify it's running:

```bash
kubectl get pods -n kube-system -l app.kubernetes.io/name=sealed-secrets
```

---

## Step 3: Create Your Secret Manifest

Create a plaintext secret file (DO NOT COMMIT THIS):

```bash
cat > k8s/02-secret.yaml <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: todo-secrets
  namespace: todo-app
type: Opaque
stringData:
  # Database connection
  database-url: "postgresql://user:password@host:5432/dbname?sslmode=require"
  
  # OpenAI API key
  openai-api-key: "sk-proj-your-api-key-here"
  
  # Auth secrets
  better-auth-secret: "your-secret-key-min-32-characters-long"
  
  # ChatKit domain key
  openai-chatkit-domain-key: "domain_pk_your-domain-key"
EOF
```

**⚠️ IMPORTANT:** Add this file to `.gitignore` immediately:

```bash
echo "k8s/02-secret.yaml" >> .gitignore
git add .gitignore
git commit -m "Add secret file to gitignore"
```

---

## Step 4: Seal Your Secret

Run the sealing script:

```bash
./k8s/seal-secret.sh
```

This will:
1. Check if `kubeseal` is installed
2. Verify cluster connection
3. Check if controller is running
4. Encrypt `k8s/02-secret.yaml` → `k8s/02-sealed-secret.yaml`

**Manual method (if script fails):**

```bash
kubeseal --format yaml < k8s/02-secret.yaml > k8s/02-sealed-secret.yaml
```

---

## Step 5: Verify the SealedSecret

Check the generated file:

```bash
cat k8s/02-sealed-secret.yaml
```

You should see an encrypted `SealedSecret` resource with `encryptedData` field.

**Test decryption (optional):**

```bash
# Apply to cluster
kubectl apply -f k8s/02-sealed-secret.yaml

# Wait a moment for controller to process
sleep 5

# Check if regular Secret was created
kubectl get secret todo-secrets -n todo-app

# Verify the secret data (base64 encoded)
kubectl get secret todo-secrets -n todo-app -o jsonpath='{.data}'
```

---

## Step 6: Commit to Git

Now it's safe to commit:

```bash
# Add the sealed secret (safe for Git)
git add k8s/02-sealed-secret.yaml

# Remove plaintext secret from git (if it was ever committed)
git rm --cached k8s/02-secret.yaml

# Commit
git commit -m "Add sealed secrets for secure credential management"

# Push
git push origin your-branch
```

---

## Step 7: Deploy to Cluster

Apply the sealed secret to your cluster:

```bash
kubectl apply -f k8s/02-sealed-secret.yaml
```

The controller will automatically:
1. Decrypt the SealedSecret
2. Create a regular Secret with the same name/namespace
3. Your deployments can now reference it

---

## Updating Secrets

To update secrets later:

```bash
# 1. Edit the plaintext secret
nano k8s/02-secret.yaml

# 2. Re-seal it
./k8s/seal-secret.sh

# 3. Apply to cluster
kubectl apply -f k8s/02-sealed-secret.yaml

# 4. Restart pods to pick up new secrets
kubectl rollout restart deployment/backend-deployment -n todo-app
kubectl rollout restart deployment/frontend-deployment -n todo-app
```

---

## Troubleshooting

### "kubeseal: command not found"

```bash
# Check if installed
which kubeseal

# Add to PATH if installed locally
export PATH=$PATH:$HOME/.local/bin
```

### "Cannot connect to Kubernetes cluster"

```bash
# Check cluster status
kubectl cluster-info

# Check context
kubectl config current-context

# List contexts
kubectl config get-contexts
```

### "SealedSecrets controller not found"

```bash
# Install controller
kubectl apply -f k8s/sealed-secrets-controller.yaml

# Wait for it to be ready
kubectl wait --for=condition=available --timeout=60s \
  -n kube-system deployment/sealed-secrets-controller
```

### "Failed to fetch public key"

```bash
# Delete controller pods (they'll regenerate keys)
kubectl delete pods -n kube-system -l app.kubernetes.io/name=sealed-secrets

# Wait for new pods to start
kubectl wait --for=condition=ready -n kube-system \
  -l app.kubernetes.io/name=sealed-secrets --timeout=120s
```

### "Secret not being created from SealedSecret"

```bash
# Check controller logs
kubectl logs -n kube-system -l app.kubernetes.io/name=sealed-secrets

# Check SealedSecret status
kubectl get sealedsecret todo-secrets -n todo-app -o yaml

# Check for events
kubectl describe sealedsecret todo-secrets -n todo-app
```

---

## Backup Controller Keys (IMPORTANT!)

The controller generates encryption keys. **Back them up** or you won't be able to decrypt secrets:

```bash
# Export keys to a file
kubectl get secret -n kube-system \
  -l sealedsecrets.bitnami.com/sealed-secrets-key \
  -o yaml > sealed-secrets-keys-backup.yaml

# Store this file safely (NOT in Git!)
```

To restore keys on a new cluster:

```bash
kubectl apply -f sealed-secrets-keys-backup.yaml
kubectl rollout restart deployment/sealed-secrets-controller -n kube-system
```

---

## Security Best Practices

1. ✅ **DO** commit `*-sealed-secret.yaml` files to Git
2. ✅ **DO** add `*-secret.yaml` (plaintext) to `.gitignore`
3. ✅ **DO** backup controller keys
4. ✅ **DO** rotate secrets regularly
5. ❌ **DON'T** commit plaintext secrets
6. ❌ **DON'T** share controller keys publicly
7. ❌ **DON'T** use the same secrets across environments

---

## Quick Reference

```bash
# Install kubeseal
wget https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/kubeseal-0.24.0-linux-amd64.tar.gz
tar -xzf kubeseal-0.24.0-linux-amd64.tar.gz
sudo install kubeseal /usr/local/bin/

# Install controller
kubectl apply -f k8s/sealed-secrets-controller.yaml

# Create secret (plaintext - DO NOT COMMIT)
kubectl create secret generic todo-secrets \
  --from-literal=database-url="postgresql://..." \
  --from-literal=openai-api-key="sk-..." \
  --dry-run=client -o yaml > k8s/02-secret.yaml

# Seal it
kubeseal --format yaml < k8s/02-secret.yaml > k8s/02-sealed-secret.yaml

# Deploy
kubectl apply -f k8s/02-sealed-secret.yaml

# Verify
kubectl get secret todo-secrets -n todo-app
```
