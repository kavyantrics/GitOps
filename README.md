# GitOps Platform Engineering Project

A production-style GitOps implementation showcasing modern DevOps and Platform Engineering practices using Kubernetes, Terraform, GitHub Actions, Jenkins, ArgoCD, and observability tooling.

This project simulates how an internal platform team designs, builds, and operates infrastructure and application delivery systems at scale.

---

## 🧠 Project Goals

- Implement **true GitOps** (Git as the single source of truth)
- Separate **application, infrastructure, and deployment concerns**
- Use **both modern and legacy CI tools** for real-world exposure
- Operate **multiple Kubernetes environments**
- Build **observable, reproducible, and auditable systems**

---

## 🏗️ Architecture Overview

```text
Developer
  ↓
Application Repository (GitHub)
  ↓
CI (GitHub Actions / Jenkins)
  ↓
Docker Image → Amazon ECR
  ↓
GitOps Repository (Manifests / Helm)
  ↓
ArgoCD
  ↓
Kubernetes (EKS / kOps / Minikube)
  ↓
Prometheus → Grafana → Alerts
```

---

## 🧰 Tech Stack

### Application

- Node.js / FastAPI backend
- Dockerized microservice
- Health & metrics endpoints

### CI/CD

- GitHub Actions (primary CI)
- Jenkins (legacy / enterprise CI)
- Docker image build & push to ECR

### Infrastructure

- Terraform (AWS infrastructure)
- Ansible (server bootstrap & config)
- Amazon EKS (managed Kubernetes)
- kOps (self-hosted Kubernetes)
- Minikube (local development)

### GitOps

- ArgoCD
- Helm charts & Kubernetes manifests
- Environment-based configuration

### Observability

- Prometheus
- Grafana
- Alertmanager
- Optional: Loki for logs

### Automation

- Python (AWS automation & maintenance scripts)

---

## 📁 Repository Structure (Monorepo)

This is a **monorepo** containing all components. See [STRUCTURE.md](./STRUCTURE.md) for monorepo vs multi-repo discussion.

```
GitOps/
├── app/                          # Application code
│   ├── backend/                  # Node.js/TypeScript backend
│   │   ├── src/
│   │   ├── Dockerfile
│   │   └── package.json
│   └── frontend/                 # Next.js frontend
│       ├── src/
│       ├── Dockerfile
│       └── package.json
├── infrastructure/               # Infrastructure as Code
│   ├── terraform/                # Terraform modules
│   │   ├── vpc/
│   │   ├── eks/
│   │   ├── ecr/
│   │   └── iam/
│   └── ansible/                  # Ansible playbooks
│       ├── common.yml
│       ├── jenkins.yml
│       └── monitoring.yml
├── gitops/                       # GitOps manifests (ArgoCD)
│   ├── clusters/                 # Cluster-specific configs
│   │   ├── eks-prod/
│   │   ├── kops-dev/
│   │   └── minikube-local/
│   └── helm/                     # Helm charts
│       └── app-chart/
├── .github/workflows/             # GitHub Actions CI/CD
│   ├── ci.yaml
│   └── terraform.yml
├── jenkins/                       # Jenkins pipelines
│   └── Jenkinsfile
└── automation/                    # Python automation scripts
    ├── cleanup_ecr.py
    ├── cost_report.py
    └── health_check.py
```

---

## 🔄 GitOps Workflow

1. Developer pushes code to application-repo
2. CI pipeline runs tests & builds Docker image
3. Image is pushed to Amazon ECR
4. CI updates image tag in gitops-repo
5. ArgoCD detects Git change
6. Kubernetes state reconciles automatically

> **Note:** CI never deploys directly to Kubernetes.

---

## 🖥️ Infrastructure Details

### AWS Resources

| Resource | Purpose |
|----------|---------|
| VPC | Network isolation |
| EKS | Production cluster |
| ECR | Container registry |
| EC2 | Jenkins, Ansible, kOps |
| S3 + DynamoDB | Terraform remote state |

### EC2 Layout

| Instance | Purpose |
|----------|---------|
| t3.medium | Jenkins |
| t3.micro | Ansible / Bastion |
| t3.medium x2 | kOps cluster |
| t3.micro | Monitoring (optional) |

---

## 📊 Monitoring & Alerts

- Cluster health dashboards
- Pod CPU & memory usage
- Application latency metrics

### Alerts for:

- Pod crash loops
- Node failures
- Resource exhaustion

---

## 🐍 Python Automation Examples

- Cleanup unused ECR images
- Cost reporting
- Health verification scripts
- Automated maintenance jobs

---

## 🔐 Security Practices

- IAM roles with least privilege
- No secrets committed to Git
- Kubernetes secrets managed via values
- Immutable Docker images
- RBAC enforced in clusters

---

## 📌 Key Learnings

- GitOps eliminates configuration drift
- CI/CD must be decoupled from deployment
- Observability is mandatory, not optional
- Platform engineering is about systems, not tools

---

## 🚀 Future Improvements

- Add service mesh (Istio / Linkerd)
- Canary & blue-green deployments
- OPA / Kyverno policies
- External secrets integration
- Chaos engineering experiments

---

## 📄 License

MIT
