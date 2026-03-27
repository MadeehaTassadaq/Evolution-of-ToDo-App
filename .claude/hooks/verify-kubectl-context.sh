#!/bin/bash
# Verify kubectl context before running kubectl commands
# This hook ensures the user is aware of their current kubectl context

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "⚠️  kubectl is not installed. Install it first: https://kubernetes.io/docs/tasks/tools/"
    exit 0
fi

# Check if a kubeconfig exists
if [[ ! -f "$HOME/.kube/config" ]] && [[ -z "$KUBECONFIG" ]]; then
    echo "⚠️  No kubeconfig found. Configure kubectl access to your cluster first."
    exit 0
fi

# Get current context (suppress errors if no context is set)
CURRENT_CONTEXT=$(kubectl config current-context 2>/dev/null)

if [[ -z "$CURRENT_CONTEXT" ]]; then
    echo "⚠️  No kubectl context is set. Set a context with: kubectl config use-context <context-name>"
    exit 0
fi

# Get cluster info for the current context
CLUSTER_NAME=$(kubectl config view --minify --output 'jsonpath={.contexts[?(@.name=="'"$CURRENT_CONTEXT"'")].context.cluster}' 2>/dev/null)
NAMESPACE=$(kubectl config view --minify --output 'jsonpath={.contexts[?(@.name=="'"$CURRENT_CONTEXT"'")].context.namespace}' 2>/dev/null)

# Display context info if it's a production-like cluster name
if [[ "$CLUSTER_NAME" =~ (prod|production|live) ]]; then
    echo "⚠️  WARNING: You are connected to a PRODUCTION cluster: $CLUSTER_NAME"
    echo "   Current namespace: ${NAMESPACE:-default}"
    echo "   Double-check your commands before applying changes!"
fi

exit 0
