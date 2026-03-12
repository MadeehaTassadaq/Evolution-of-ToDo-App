#!/bin/bash
# Script to convert Kubernetes Secret to SealedSecret
# Usage: ./k8s/seal-secret.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SECRET_FILE="${SCRIPT_DIR}/02-secret.yaml"
SEALED_FILE="${SCRIPT_DIR}/02-sealed-secret.yaml"

echo "🔐 Sealed Secrets Setup"
echo "========================"

# Check if kubeseal is installed
if ! command -v kubeseal &> /dev/null; then
    # Try user local bin
    if [ -f ~/.local/bin/kubeseal ]; then
        KUBESEAL=~/.local/bin/kubeseal
    else
        echo "❌ kubeseal not found. Install it first:"
        echo "   wget https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/kubeseal-0.24.0-linux-amd64.tar.gz"
        echo "   tar -xzf kubeseal-0.24.0-linux-amd64.tar.gz"
        echo "   sudo install kubeseal /usr/local/bin/"
        exit 1
    fi
else
    KUBESEAL=kubeseal
fi

echo "✅ Found kubeseal: $($KUBESEAL --version)"

# Check if cluster is accessible
if ! kubectl get nodes &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster."
    echo ""
    echo "Please ensure:"
    echo "  1. Your cluster is running (Docker Desktop, Minikube, or cloud K8s)"
    echo "  2. kubectl is configured correctly"
    echo "  3. Sealed Secrets controller is installed"
    echo ""
    echo "Install controller first:"
    echo "  kubectl apply -f k8s/sealed-secrets-controller.yaml"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "✅ Cluster connection verified"

# Check if controller is running
if ! kubectl get deployment -n kube-system sealed-secrets-controller &> /dev/null; then
    echo "⚠️  Sealed Secrets controller not found."
    echo ""
    echo "Install it first:"
    echo "  kubectl apply -f ${SCRIPT_DIR}/sealed-secrets-controller.yaml"
    echo ""
    echo "Waiting for controller to be ready..."
    kubectl apply -f "${SCRIPT_DIR}/sealed-secrets-controller.yaml"
    kubectl wait --for=condition=available -n kube-system deployment/sealed-secrets-controller --timeout=60s
fi

echo "✅ Sealed Secrets controller is running"

# Check if secret file exists
if [ ! -f "$SECRET_FILE" ]; then
    echo "❌ Secret file not found: $SECRET_FILE"
    exit 1
fi

echo "📄 Reading secret from: $SECRET_FILE"

# Create sealed secret
echo ""
echo "🔒 Creating SealedSecret..."
$KUBESEAL --format yaml < "$SECRET_FILE" > "$SEALED_FILE"

if [ $? -eq 0 ]; then
    echo "✅ SealedSecret created: $SEALED_FILE"
    echo ""
    echo "📋 SealedSecret contents (encrypted, safe for Git):"
    echo "---"
    head -20 "$SEALED_FILE"
    echo "---"
    echo ""
    echo "✨ You can now safely commit $SEALED_FILE to Git!"
    echo ""
    echo "📌 Next steps:"
    echo "  1. Commit the sealed secret:"
    echo "     git add k8s/02-sealed-secret.yaml"
    echo "     git commit -m 'Add sealed secrets'"
    echo ""
    echo "  2. Delete the original secret from Git history:"
    echo "     git rm --cached k8s/02-secret.yaml"
    echo "     git commit -m 'Remove plaintext secret'"
    echo ""
    echo "  3. Deploy to cluster:"
    echo "     kubectl apply -f k8s/02-sealed-secret.yaml"
else
    echo "❌ Failed to create SealedSecret"
    exit 1
fi
