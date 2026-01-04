# ArgoCD Configuration

This directory contains ArgoCD installation and configuration files.

## Files

- **install.sh**: Script to install ArgoCD using Helm
- **values.yaml**: Helm values for customizing ArgoCD installation
- **app-project.yaml**: ArgoCD AppProject for organizing applications
- **repository.yaml**: Git repository credentials for ArgoCD
- **install.yaml**: Documentation for manual installation

## Quick Start

### 1. Install ArgoCD

**Option A: Using the installation script (Recommended)**
```bash
chmod +x gitops/argocd/install.sh
./gitops/argocd/install.sh
```

**Option B: Using Helm manually**
```bash
kubectl create namespace argocd
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
helm install argocd argo/argo-cd \
  --namespace argocd \
  --values gitops/argocd/values.yaml
```

**Option C: Using kubectl (Official manifests)**
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### 2. Get ArgoCD Admin Password

```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

### 3. Access ArgoCD UI

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Then open: https://localhost:8080
- Username: `admin`
- Password: (from step 2)

### 4. Configure ArgoCD

Apply the configuration files:

```bash
# Create AppProject
kubectl apply -f gitops/argocd/app-project.yaml

# Configure repository (update with your repo URL and credentials)
kubectl apply -f gitops/argocd/repository.yaml

# Create Applications
kubectl apply -f gitops/clusters/eks-prod/application.yaml
kubectl apply -f gitops/clusters/kops-dev/application.yaml
kubectl apply -f gitops/clusters/minikube-local/application.yaml
```

## Configuration Details

### AppProject

The `app-project.yaml` defines:
- **Source repositories**: Which Git repos ArgoCD can access
- **Destinations**: Which clusters and namespaces apps can deploy to
- **RBAC**: Permissions for different roles

### Repository Configuration

The `repository.yaml` contains Git repository credentials. For production:
- Use **GitHub App** authentication (recommended)
- Or use **SSH keys** for private repos
- Never commit actual credentials - use sealed-secrets or external-secrets operator

### Application Manifests

Each cluster has an `application.yaml` that defines:
- **Source**: Git repo URL and path
- **Destination**: Target cluster and namespace
- **Sync Policy**: Automated sync, self-heal, prune settings

The actual Kubernetes resources are in `app-resources.yaml` in each cluster directory.

## ArgoCD CLI

Install ArgoCD CLI for command-line operations:

```bash
# macOS
brew install argocd

# Linux
curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
chmod +x /usr/local/bin/argocd

# Login
argocd login localhost:8080
```

## Common Commands

```bash
# List applications
argocd app list

# Get application status
argocd app get gitops-app-prod

# Sync application manually
argocd app sync gitops-app-prod

# Watch application sync
argocd app wait gitops-app-prod

# Get application logs
argocd app logs gitops-app-prod
```

## Troubleshooting

### ArgoCD not syncing

1. Check application status:
```bash
kubectl get applications -n argocd
kubectl describe application gitops-app-prod -n argocd
```

2. Check ArgoCD controller logs:
```bash
kubectl logs -n argocd deployment/argocd-application-controller
```

3. Verify repository access:
```bash
argocd repo list
argocd repo get https://github.com/your-org/gitops-platform.git
```

### Repository authentication issues

1. Check repository secret:
```bash
kubectl get secret -n argocd -l argocd.argoproj.io/secret-type=repository
```

2. Test repository connection:
```bash
argocd repo add https://github.com/your-org/gitops-platform.git --type git
```

### Application stuck in Syncing

1. Check for sync errors:
```bash
argocd app get gitops-app-prod
```

2. Check resource conflicts:
```bash
kubectl get all -n production
```

3. Force refresh:
```bash
argocd app refresh gitops-app-prod --hard
```

## Security Best Practices

1. **Change default admin password**:
```bash
argocd account update-password
```

2. **Use RBAC**: Configure proper roles and permissions in AppProject

3. **Secure repository credentials**: Use sealed-secrets or external-secrets

4. **Enable TLS**: Configure ingress with TLS certificates

5. **Limit access**: Use network policies to restrict ArgoCD access

## Resources

- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [ArgoCD Best Practices](https://argo-cd.readthedocs.io/en/stable/user-guide/best_practices/)
- [ArgoCD Helm Chart](https://github.com/argoproj/argo-helm/tree/main/charts/argo-cd)

