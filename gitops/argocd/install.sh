#!/bin/bash
# ArgoCD Installation Script
# This script installs ArgoCD using Helm

set -e

echo "🚀 Installing ArgoCD..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if helm is available
if ! command -v helm &> /dev/null; then
    echo "❌ Helm is not installed. Please install Helm first."
    exit 1
fi

# Create namespace
echo "📦 Creating argocd namespace..."
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -

# Add ArgoCD Helm repository
echo "📚 Adding ArgoCD Helm repository..."
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

# Install ArgoCD
echo "⬇️  Installing ArgoCD..."
helm install argocd argo/argo-cd \
  --namespace argocd \
  --version 7.4.0 \
  --values gitops/argocd/values.yaml \
  --wait

# Wait for ArgoCD to be ready
echo "⏳ Waiting for ArgoCD to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n argocd || true
kubectl wait --for=condition=available --timeout=300s deployment/argocd-application-controller -n argocd || true
kubectl wait --for=condition=available --timeout=300s deployment/argocd-repo-server -n argocd || true

# Get initial admin password
echo ""
echo "🔐 Getting ArgoCD admin password..."
ARGOCD_PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)

echo ""
echo "✅ ArgoCD installed successfully!"
echo ""
echo "📋 Access Information:"
echo "   Username: admin"
echo "   Password: $ARGOCD_PASSWORD"
echo ""
echo "🌐 To access ArgoCD UI:"
echo "   kubectl port-forward svc/argocd-server -n argocd 8080:443"
echo "   Then open: https://localhost:8080"
echo ""
echo "📝 Next steps:"
echo "   1. Apply AppProject: kubectl apply -f gitops/argocd/app-project.yaml"
echo "   2. Apply Repository: kubectl apply -f gitops/argocd/repository.yaml"
echo "   3. Apply Applications: kubectl apply -f gitops/clusters/*/application.yaml"
echo ""

