# GitOps Repository

This directory contains Kubernetes manifests and Helm charts that ArgoCD will sync to clusters.

## Structure

```
gitops/
├── argocd/                    # ArgoCD installation and configuration
│   ├── install.sh            # Installation script
│   ├── values.yaml           # Helm values
│   ├── app-project.yaml      # AppProject definition
│   ├── repository.yaml       # Git repository credentials
│   └── README.md             # ArgoCD setup guide
├── clusters/                  # Cluster-specific configurations
│   ├── eks-prod/             # Production EKS cluster
│   │   ├── application.yaml  # ArgoCD Application CRD
│   │   └── app-resources.yaml # Kubernetes resources
│   ├── kops-dev/             # Development kOps cluster
│   │   ├── application.yaml
│   │   └── app-resources.yaml
│   └── minikube-local/       # Local Minikube
│       ├── application.yaml
│       └── app-resources.yaml
└── helm/                      # Helm charts
    └── app-chart/            # Reusable Helm chart
```

## GitOps Workflow

1. **CI Pipeline** builds Docker image and pushes to ECR
2. **CI updates** image tag in `app-resources.yaml` files
3. **ArgoCD detects** the Git change (polls every 3 minutes by default)
4. **ArgoCD syncs** the new configuration to Kubernetes automatically
5. **Kubernetes reconciles** to desired state

## ArgoCD Setup

See [argocd/README.md](./argocd/README.md) for complete installation instructions.

### Quick Install

```bash
# Install ArgoCD
./gitops/argocd/install.sh

# Configure ArgoCD
kubectl apply -f gitops/argocd/app-project.yaml
kubectl apply -f gitops/argocd/repository.yaml

# Create Applications
kubectl apply -f gitops/clusters/*/application.yaml
```

### Application Structure

Each cluster directory contains:
- **application.yaml**: ArgoCD Application CRD that defines what to sync
- **app-resources.yaml**: Actual Kubernetes resources (Deployments, Services, etc.)

The Application CRD points to the directory path, and ArgoCD syncs all YAML files in that path.

## Environment-Specific Configurations

- **eks-prod**: Production settings (3 replicas, HPA, resource limits, LoadBalancer)
- **kops-dev**: Development settings (2 replicas, lower resources, ClusterIP)
- **minikube-local**: Local testing (1 replica, NodePort on 30080)

## How It Works

1. **ArgoCD Application** (`application.yaml`) is a Kubernetes CRD that tells ArgoCD:
   - Which Git repository to watch
   - Which path in the repo contains manifests
   - Which cluster/namespace to deploy to
   - Sync policy (automated, self-heal, prune)

2. **Kubernetes Resources** (`app-resources.yaml`) contain the actual:
   - Deployments
   - Services
   - ConfigMaps
   - Secrets
   - Any other K8s resources

3. **ArgoCD Controller** continuously:
   - Monitors Git repository for changes
   - Compares Git state with cluster state
   - Syncs differences automatically (if enabled)

## Updating Applications

When CI updates the image tag in `app-resources.yaml`:

```yaml
image: <ECR_REPO_URL>:<NEW_TAG>
```

ArgoCD will:
1. Detect the change (within 3 minutes)
2. Show the diff in UI/CLI
3. Automatically sync (if `automated.sync` is enabled)
4. Update the Deployment with new image
5. Kubernetes will perform rolling update

## Manual Sync

You can also sync manually:

```bash
# Using kubectl
kubectl patch application gitops-app-prod -n argocd --type merge -p '{"operation":{"initiatedBy":{"username":"admin"},"sync":{"revision":"main"}}}'

# Using ArgoCD CLI
argocd app sync gitops-app-prod
```

