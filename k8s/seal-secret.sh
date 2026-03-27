#!/bin/bash
# Script to convert Kubernetes Secret to SealedSecret
# Usage: ./k8s/seal-secret.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SECRET_FILE="${SCRIPT_DIR}/02-secret.yaml"
SEALED_FILE="${SCRIPT_DIR}/02-sealed-secret.yaml"

echo "🔐 Sealed Secrets Setup"
echo "========================"
echo ""

# Check if kubeseal is installed
KUBESEAL=""
if command -v kubeseal &> /dev/null; then
    KUBESEAL=kubeseal
elif [ -f ~/.local/bin/kubeseal ]; then
    KUBESEAL=~/.local/bin/kubeseal
elif [ -f "$PROJECT_ROOT/kubeseal" ]; then
    KUBESEAL="$PROJECT_ROOT/kubeseal"
else
    echo "❌ kubeseal not found. Install it first:"
    echo ""
    echo "   # Download and extract:"
    echo "   cd $PROJECT_ROOT"
    echo "   tar -xzf kubeseal-0.24.0-linux-amd64.tar.gz"
    echo "   sudo install kubeseal /usr/local/bin/"
    echo ""
    echo "   # Or install to user local (no sudo):"
    echo "   mkdir -p ~/.local/bin"
    echo "   install kubeseal ~/.local/bin/kubeseal"
    echo "   export PATH=\$PATH:\$HOME/.local/bin"
    echo ""
    exit 1
fi

echo "✅ Found kubeseal: $($KUBESEAL --version)"
echo ""

# Check if cluster is accessible
echo "🔍 Checking Kubernetes cluster connection..."
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster."
    echo ""
    echo "Please ensure:"
    echo "  1. Your cluster is running (Docker Desktop, Minikube, DOKS, etc.)"
    echo "  2. kubectl is configured correctly"
    echo ""
    echo "Check cluster status:"
    echo "  kubectl cluster-info"
    echo ""
    echo "List contexts:"
    echo "  kubectl config get-contexts"
    echo ""
    exit 1
fi

CURRENT_CONTEXT=$(kubectl config current-context 2>/dev/null || echo "unknown")
echo "✅ Connected to cluster (context: $CURRENT_CONTEXT)"
echo ""

# Check if controller is running
echo "🔍 Checking Sealed Secrets controller..."
if ! kubectl get deployment -n kube-system sealed-secrets-controller &> /dev/null; then
    echo "⚠️  Sealed Secrets controller not found."
    echo ""
    echo "Installing controller..."
    kubectl apply -f "${SCRIPT_DIR}/sealed-secrets-controller.yaml"
    echo ""
    echo "Waiting for controller to be ready (up to 60 seconds)..."
    if kubectl wait --for=condition=available -n kube-system deployment/sealed-secrets-controller --timeout=60s; then
        echo "✅ Sealed Secrets controller is running"
    else
        echo "⚠️  Controller installation may still be in progress..."
        echo "   Check status: kubectl get pods -n kube-system -l app.kubernetes.io/name=sealed-secrets"
    fi
else
    CONTROLLER_STATUS=$(kubectl get deployment -n kube-system sealed-secrets-controller -o jsonpath='{.status.availableReplicas}')
    if [ "$CONTROLLER_STATUS" -gt 0 ]; then
        echo "✅ Sealed Secrets controller is running"
    else
        echo "⚠️  Controller exists but no replicas are available"
        echo "   Check status: kubectl get pods -n kube-system -l app.kubernetes.io/name=sealed-secrets"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi
echo ""

# Check if secret file exists
if [ ! -f "$SECRET_FILE" ]; then
    echo "❌ Secret file not found: $SECRET_FILE"
    echo ""
    echo "📝 Create it first with your credentials:"
    echo "   cat > $SECRET_FILE <<EOF"
    echo "   apiVersion: v1"
    echo "   kind: Secret"
    echo "   metadata:"
    echo "     name: todo-secrets"
    echo "     namespace: todo-app"
    echo "   type: Opaque"
    echo "   stringData:"
    echo "     database-url: \"postgresql://...\""
    echo "     openai-api-key: \"sk-proj-...\""
    echo "     better-auth-secret: \"your-secret-key\""
    echo "   EOF"
    echo ""
    echo "⚠️  IMPORTANT: Add this file to .gitignore!"
    echo "   echo 'k8s/02-secret.yaml' >> .gitignore"
    echo ""
    exit 1
fi

echo "📄 Reading secret from: $SECRET_FILE"

# Validate secret file has content
if ! grep -q "kind: Secret" "$SECRET_FILE"; then
    echo "❌ Invalid secret file format. Should be a Kubernetes Secret YAML."
    exit 1
fi

# Check if secret contains sensitive placeholders
if grep -q "YOUR_PASSWORD\|your-openai-api-key-here\|your-secret-key-here" "$SECRET_FILE"; then
    echo "⚠️  Warning: Secret file contains placeholder values."
    echo "   Make sure to replace them with real values before sealing!"
    read -p "Continue with placeholders? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create sealed secret
echo ""
echo "🔒 Creating SealedSecret..."
if $KUBESEAL --format yaml < "$SECRET_FILE" > "$SEALED_FILE" 2>&1; then
    echo "✅ SealedSecret created: $SEALED_FILE"
    echo ""
    echo "📋 SealedSecret preview (encrypted, safe for Git):"
    echo "---"
    head -25 "$SEALED_FILE"
    echo "---"
    echo ""
    echo "✨ You can now safely commit $SEALED_FILE to Git!"
    echo ""
    echo "📌 Next steps:"
    echo ""
    echo "  1. ✅ Commit the sealed secret:"
    echo "     git add k8s/02-sealed-secret.yaml"
    echo "     git commit -m 'Add sealed secrets for secure credential management'"
    echo ""
    echo "  2. 🗑️  Remove plaintext secret from Git (if tracked):"
    echo "     git rm --cached k8s/02-secret.yaml"
    echo "     git commit -m 'Remove plaintext secret from version control'"
    echo ""
    echo "  3. 📦 Deploy to cluster:"
    echo "     kubectl apply -f k8s/02-sealed-secret.yaml"
    echo ""
    echo "  4. ✅ Verify secret was created:"
    echo "     kubectl get secret todo-secrets -n todo-app"
    echo ""
else
    echo "❌ Failed to create SealedSecret"
    echo ""
    echo "Error details:"
    cat "$SEALED_FILE"
    rm -f "$SEALED_FILE"
    exit 1
fi
