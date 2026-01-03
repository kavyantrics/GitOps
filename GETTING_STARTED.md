# Getting Started with GitOps Platform

This guide will help you set up and deploy the GitOps platform from scratch.

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured (`aws configure`)
- Terraform >= 1.0
- Ansible >= 2.9
- kubectl installed
- Docker installed
- Node.js 20+ (for local development)
- Python 3.9+ (for automation scripts)

## Step 1: Clone and Setup

```bash
git clone <your-repo-url>
cd GitOps
```

## Step 2: Configure AWS

1. Set up AWS credentials:
```bash
aws configure
```

2. Create S3 bucket for Terraform state:
```bash
aws s3 mb s3://your-terraform-state-bucket
aws s3api put-bucket-versioning \
  --bucket your-terraform-state-bucket \
  --versioning-configuration Status=Enabled
```

3. Create DynamoDB table for state locking:
```bash
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
```

## Step 3: Deploy Infrastructure

### 3.1 Deploy VPC

```bash
cd infrastructure/terraform/vpc
terraform init
terraform plan
terraform apply
```

Note the VPC ID and subnet IDs from outputs.

### 3.2 Deploy IAM

```bash
cd ../iam
terraform init
terraform plan
terraform apply
```

### 3.3 Deploy ECR

```bash
cd ../ecr
terraform init
terraform plan
terraform apply
```

Note the ECR repository URL from outputs.

### 3.4 Deploy EKS

```bash
cd ../eks
# Update variables.tf with VPC ID and subnet IDs from VPC module
terraform init
terraform plan
terraform apply
```

Configure kubectl:
```bash
aws eks update-kubeconfig --name gitops-eks-prod --region us-east-1
```

## Step 4: Setup EC2 Instances

1. Launch EC2 instances:
   - t3.medium for Jenkins
   - t3.micro for Ansible/Bastion
   - t3.medium x2 for kOps cluster

2. Update Ansible inventory:
```bash
cd infrastructure/ansible
cp inventory/prod.yml.example inventory/prod.yml
# Edit prod.yml with your EC2 instance IPs
```

3. Run Ansible playbooks:
```bash
ansible-playbook -i inventory/prod.yml common.yml
ansible-playbook -i inventory/prod.yml jenkins.yml
ansible-playbook -i inventory/prod.yml monitoring.yml
```

## Step 5: Install ArgoCD

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for ArgoCD to be ready
kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n argocd

# Get ArgoCD admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

Access ArgoCD UI:
```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
# Open https://localhost:8080
# Username: admin
# Password: (from above command)
```

## Step 6: Configure ArgoCD

1. In ArgoCD UI, create a new application:
   - Name: `gitops-app-prod`
   - Repository URL: `https://github.com/your-org/gitops-platform.git`
   - Path: `gitops/clusters/eks-prod`
   - Cluster: `in-cluster`
   - Namespace: `production`

2. Or use the Application manifest in `gitops/clusters/eks-prod/app.yaml`

## Step 7: Configure CI/CD

### GitHub Actions

1. Add secrets to GitHub repository:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_ACCOUNT_ID`

2. Update `.github/workflows/ci.yaml` with your ECR repository URL

3. Push to main branch - CI will:
   - Run tests
   - Build Docker image
   - Push to ECR
   - Update GitOps manifests

### Jenkins (Alternative)

1. Access Jenkins UI (configured via Ansible)
2. Create new pipeline job
3. Point to `jenkins/Jenkinsfile`
4. Configure AWS credentials in Jenkins

## Step 8: Deploy Application

1. Push code to trigger CI:
```bash
git add .
git commit -m "Initial deployment"
git push origin main
```

2. CI will build and push Docker image to ECR

3. CI will update image tag in `gitops/clusters/eks-prod/app.yaml`

4. ArgoCD will detect the change and sync to Kubernetes

5. Verify deployment:
```bash
kubectl get pods -n production
kubectl get services -n production
```

## Step 9: Setup Monitoring

1. Install Prometheus:
```bash
kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/bundle.yaml
```

2. Install Grafana:
```bash
kubectl apply -f https://raw.githubusercontent.com/grafana/helm-charts/main/charts/grafana/values.yaml
```

3. Access Grafana:
```bash
kubectl port-forward svc/grafana -n monitoring 3000:3000
# Open http://localhost:3000
```

## Step 10: Run Automation Scripts

```bash
cd automation
pip install -r requirements.txt

# Health check
python health_check.py --namespace production

# Cost report
python cost_report.py --days 30

# ECR cleanup (dry run)
python cleanup_ecr.py --repository gitops-app --days 30 --keep-latest 10
```

## Troubleshooting

### ArgoCD not syncing

```bash
kubectl logs -n argocd deployment/argocd-application-controller
kubectl get applications -n argocd
```

### Pods not starting

```bash
kubectl describe pod <pod-name> -n production
kubectl logs <pod-name> -n production
```

### ECR push fails

Check AWS credentials and IAM permissions:
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
```

## Next Steps

- Add service mesh (Istio/Linkerd)
- Implement canary deployments
- Add OPA/Kyverno policies
- Set up external secrets
- Configure alerting rules

## Resources

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

