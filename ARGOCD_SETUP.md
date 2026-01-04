# ArgoCD Setup Guide

Complete guide to setting up and using ArgoCD in this GitOps platform.

## What is ArgoCD?

ArgoCD is a declarative, GitOps continuous delivery tool for Kubernetes. It:
- Monitors Git repositories for changes
- Automatically syncs Kubernetes resources
- Provides a UI and CLI for managing deployments
- Enforces Git as the single source of truth

## Architecture

```
Git Repository (GitHub)
    ↓
ArgoCD (watches Git)
    ↓
Kubernetes Cluster (EKS/kOps/Minikube)
```

## Installation

### Prerequisites

- Kubernetes cluster running (EKS, kOps, or Minikube)
- `kubectl` configured to access the cluster
- `helm` installed (for Helm installation method)

### Method 1: Using Installation Script (Recommended)

```bash
cd gitops/argocd
chmod +x install.sh
./install.sh
```

This script will:
1. Create the `argocd` namespace
2. Add ArgoCD Helm repository
3. Install ArgoCD using Helm
4. Wait for ArgoCD to be ready
5. Display the admin password

### Method 2: Using Helm Manually

```bash
# Create namespace
kubectl create namespace argocd

# Add Helm repository
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

# Install ArgoCD
helm install argocd argo/argo-cd \
  --namespace argocd \
  --version 7.4.0 \
  --values gitops/argocd/values.yaml \
  --wait
```

### Method 3: Using Official Manifests

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

## Access ArgoCD

### Get Admin Password

```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

### Port Forward to UI

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Then open: **https://localhost:8080**
- Username: `admin`
- Password: (from above command)

### Install ArgoCD CLI (Optional)

```bash
# macOS
brew install argocd

# Linux
curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
chmod +x /usr/local/bin/argocd

# Login
argocd login localhost:8080
```

## Configuration

### 1. Create AppProject

The AppProject defines what repositories and destinations are allowed:

```bash
kubectl apply -f gitops/argocd/app-project.yaml
```

This creates a project called `gitops-platform` that:
- Allows all source repositories (restrict in production)
- Allows deployment to all namespaces
- Defines RBAC roles

### 2. Configure Repository

Update `gitops/argocd/repository.yaml` with your actual repository URL and credentials, then apply:

```bash
# For public repository (no credentials needed)
kubectl apply -f gitops/argocd/repository.yaml

# For private repository, you'll need to add credentials
# See gitops/argocd/repository.yaml for examples
```

**Important**: For production, use:
- GitHub App authentication (recommended)
- SSH keys
- Never commit actual passwords/tokens

### 3. Create Applications

Create ArgoCD Applications for each environment:

```bash
# Production
kubectl apply -f gitops/clusters/eks-prod/application.yaml

# Development
kubectl apply -f gitops/clusters/kops-dev/application.yaml

# Local
kubectl apply -f gitops/clusters/minikube-local/application.yaml
```

## Verify Installation

### Check ArgoCD Status

```bash
kubectl get pods -n argocd
kubectl get applications -n argocd
```

### Check Application Sync Status

```bash
# Using kubectl
kubectl get applications -n argocd

# Using ArgoCD CLI
argocd app list
argocd app get gitops-app-prod
```

### View in UI

1. Port forward: `kubectl port-forward svc/argocd-server -n argocd 8080:443`
2. Open https://localhost:8080
3. Login with admin credentials
4. You should see your applications listed

## How It Works

### Application Definition

Each `application.yaml` file defines:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: gitops-app-prod
spec:
  source:
    repoURL: https://github.com/your-org/gitops-platform.git
    path: gitops/clusters/eks-prod  # Path in Git repo
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true      # Delete resources removed from Git
      selfHeal: true   # Auto-sync if cluster drifts
```

### Sync Process

1. ArgoCD polls Git repository (default: every 3 minutes)
2. Compares Git state with cluster state
3. If differences found:
   - Shows diff in UI/CLI
   - Automatically syncs (if `automated` enabled)
   - Updates Kubernetes resources

### Resource Files

The `app-resources.yaml` files contain actual Kubernetes resources:
- Deployments
- Services
- ConfigMaps
- Secrets
- HPA
- etc.

When CI updates the image tag in these files, ArgoCD detects and syncs automatically.

## Common Operations

### Manual Sync

```bash
# Using CLI
argocd app sync gitops-app-prod

# Using kubectl
kubectl patch application gitops-app-prod -n argocd \
  --type merge \
  -p '{"operation":{"initiatedBy":{"username":"admin"},"sync":{"revision":"main"}}}'
```

### Refresh Application

Force ArgoCD to check Git for changes:

```bash
argocd app refresh gitops-app-prod
argocd app refresh gitops-app-prod --hard  # Hard refresh
```

### View Application Logs

```bash
argocd app logs gitops-app-prod
argocd app logs gitops-app-prod --tail 100
```

### Watch Sync

```bash
argocd app wait gitops-app-prod
```

### Rollback

```bash
argocd app rollback gitops-app-prod <history-id>
```

## Troubleshooting

### Application Not Syncing

1. **Check application status**:
```bash
kubectl describe application gitops-app-prod -n argocd
```

2. **Check ArgoCD controller logs**:
```bash
kubectl logs -n argocd deployment/argocd-application-controller
```

3. **Verify repository access**:
```bash
argocd repo list
argocd repo get https://github.com/your-org/gitops-platform.git
```

### Repository Authentication Issues

1. **Check repository secret**:
```bash
kubectl get secret -n argocd -l argocd.argoproj.io/secret-type=repository
```

2. **Test repository connection**:
```bash
argocd repo add https://github.com/your-org/gitops-platform.git --type git
```

### Application Stuck

1. **Check for sync errors**:
```bash
argocd app get gitops-app-prod
```

2. **Check resource conflicts**:
```bash
kubectl get all -n production
```

3. **Force refresh**:
```bash
argocd app refresh gitops-app-prod --hard
```

## Security Best Practices

1. **Change default password**:
```bash
argocd account update-password
```

2. **Use RBAC**: Configure roles in AppProject

3. **Secure credentials**: Use sealed-secrets or external-secrets

4. **Enable TLS**: Configure ingress with certificates

5. **Network policies**: Restrict ArgoCD access

## Next Steps

- Configure monitoring for ArgoCD
- Set up notifications (Slack, email)
- Implement sync windows
- Add sync hooks for pre/post deployment tasks
- Configure SSO authentication

## Resources

- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [ArgoCD Best Practices](https://argo-cd.readthedocs.io/en/stable/user-guide/best_practices/)
- [ArgoCD CLI Reference](https://argo-cd.readthedocs.io/en/stable/user-guide/commands/)

