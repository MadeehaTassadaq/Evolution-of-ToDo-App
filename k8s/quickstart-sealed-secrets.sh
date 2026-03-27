#!/bin/bash
# ============================================
# QUICK START: SEALED SECRETS SETUP
# ============================================
# Run this script to set up SealedSecrets in 5 minutes
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "╔════════════════════════════════════════╗"
echo "║  Sealed Secrets Quick Setup           ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Step 1: Install kubeseal
echo "📦 Step 1/5: Installing kubeseal CLI..."
if command -v kubeseal &> /dev/null; then
    echo "   ✅ kubeseal already installed"
elif [ -f "$PROJECT_ROOT/kubeseal" ]; then
    echo "   📦 Installing from project directory..."
    sudo install "$PROJECT_ROOT/kubeseal" /usr/local/bin/kubeseal
    echo "   ✅ kubeseal installed"
else
    echo "   📦 Extracting from tarball..."
    cd "$PROJECT_ROOT"
    tar -xzf kubeseal-0.24.0-linux-amd64.tar.gz
    sudo install kubeseal /usr/local/bin/kubeseal
    echo "   ✅ kubeseal installed"
fi
echo ""

# Step 2: Check cluster
echo "🔍 Step 2/5: Checking Kubernetes cluster..."
if ! kubectl cluster-info &> /dev/null; then
    echo "   ❌ Cannot connect to Kubernetes cluster"
    echo "   Please start your cluster (Docker Desktop, Kind, Minikube, etc.)"
    exit 1
fi
CURRENT_CONTEXT=$(kubectl config current-context 2>/dev/null || echo "unknown")
echo "   ✅ Connected to: $CURRENT_CONTEXT"
echo ""

# Step 3: Install controller
echo "🔧 Step 3/5: Installing Sealed Secrets controller..."
if kubectl get deployment -n kube-system sealed-secrets-controller &> /dev/null; then
    echo "   ✅ Controller already installed"
else
    kubectl apply -f "$SCRIPT_DIR/sealed-secrets-controller.yaml"
    echo "   ⏳ Waiting for controller to be ready..."
    kubectl wait --for=condition=available -n kube-system deployment/sealed-secrets-controller --timeout=60s || {
        echo "   ⚠️  Controller still starting up (this is normal)"
    }
    echo "   ✅ Controller installed"
fi
echo ""

# Step 4: Create secret template
echo "📝 Step 4/5: Creating secret template..."
if [ -f "$SCRIPT_DIR/02-secret.yaml" ]; then
    echo "   ⚠️  Secret file already exists"
    echo "   📂 Location: $SCRIPT_DIR/02-secret.yaml"
else
    cp "$SCRIPT_DIR/02-secret.template.yaml" "$SCRIPT_DIR/02-secret.yaml"
    echo "   ✅ Created: $SCRIPT_DIR/02-secret.yaml"
    echo "   📌 Edit this file with your real credentials!"
fi
echo ""

# Step 5: Seal the secret
echo "🔒 Step 5/5: Sealing the secret..."
if [ ! -f "$SCRIPT_DIR/02-secret.yaml" ]; then
    echo "   ❌ Secret file not found"
    echo "   Please edit $SCRIPT_DIR/02-secret.yaml with your credentials first"
    exit 1
fi

# Check if it has real values or placeholders
if grep -q "YOUR_PASSWORD\|your-openai-api-key-here" "$SCRIPT_DIR/02-secret.yaml"; then
    echo "   ⚠️  Secret contains placeholder values"
    echo "   Please edit $SCRIPT_DIR/02-secret.yaml with real credentials"
    echo ""
    read -p "Continue with placeholders for testing? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "   📌 When ready, run: $SCRIPT_DIR/seal-secret.sh"
        exit 0
    fi
fi

kubeseal --format yaml < "$SCRIPT_DIR/02-secret.yaml" > "$SCRIPT_DIR/02-sealed-secret.yaml"
echo "   ✅ SealedSecret created: $SCRIPT_DIR/02-sealed-secret.yaml"
echo ""

# Summary
echo "╔════════════════════════════════════════╗"
echo "║  ✅ Setup Complete!                   ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "📋 What was created:"
echo "   • k8s/02-secret.yaml (plaintext - DO NOT COMMIT)"
echo "   • k8s/02-sealed-secret.yaml (encrypted - SAFE TO COMMIT)"
echo ""
echo "📌 Next steps:"
echo ""
echo "   1. Edit k8s/02-secret.yaml with your real credentials"
echo "   2. Re-run this script or run: ./k8s/seal-secret.sh"
echo "   3. Deploy to cluster:"
echo "      kubectl apply -f k8s/02-sealed-secret.yaml"
echo "   4. Verify:"
echo "      kubectl get secret todo-secrets -n todo-app"
echo ""
echo "🔐 Security reminder:"
echo "   • NEVER commit k8s/02-secret.yaml to Git"
echo "   • It's safe to commit k8s/02-sealed-secret.yaml"
echo ""
