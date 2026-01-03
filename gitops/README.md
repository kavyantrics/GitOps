# GitOps Repository

This directory contains Kubernetes manifests and Helm charts that ArgoCD will sync to clusters.

## Structure

```
gitops/
├── clusters/
│   ├── eks-prod/        # Production EKS cluster manifests
│   ├── kops-dev/        # Development kOps cluster manifests
│   └── minikube-local/  # Local development manifests
└── helm/
    └── app-chart/       # Helm chart for the application
```

## GitOps Workflow

1. CI pipeline builds Docker image and pushes to ECR
2. CI updates image tag in this repository (e.g., `gitops/clusters/eks-prod/app.yaml`)
3. ArgoCD detects the Git change
4. ArgoCD syncs the new configuration to Kubernetes
5. Kubernetes reconciles to desired state

## ArgoCD Setup

ArgoCD watches this repository and automatically syncs changes to configured clusters.

### Application Definitions

Each cluster has an ArgoCD Application resource that defines:
- Source repository and path
- Destination cluster and namespace
- Sync policy (automated or manual)

## Environment-Specific Configurations

- **eks-prod**: Production settings (3 replicas, resource limits, LoadBalancer)
- **kops-dev**: Development settings (2 replicas, lower resources, ClusterIP)
- **minikube-local**: Local testing (1 replica, NodePort)

