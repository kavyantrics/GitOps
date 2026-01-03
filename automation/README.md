# Automation Scripts

Python scripts for maintenance and operations of the GitOps platform.

## Scripts

### cleanup_ecr.py

Cleans up old/unused Docker images from Amazon ECR.

```bash
# Dry run (default)
python automation/cleanup_ecr.py --repository gitops-app --days 30 --keep-latest 10

# Actually delete images
python automation/cleanup_ecr.py --repository gitops-app --days 30 --keep-latest 10 --execute
```

### cost_report.py

Generates AWS cost report for platform resources.

```bash
# Last 30 days (default)
python automation/cost_report.py

# Custom period
python automation/cost_report.py --days 7
```

### health_check.py

Verifies cluster health, pod status, and service availability.

```bash
# Check default namespace
python automation/health_check.py

# Check specific namespace
python automation/health_check.py --namespace production
```

## Requirements

Install dependencies:

```bash
pip install boto3 kubernetes
```

## AWS Credentials

Scripts use AWS credentials from:
- Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
- AWS credentials file (`~/.aws/credentials`)
- IAM roles (if running on EC2)

## Kubernetes Access

For `health_check.py`, ensure `kubectl` is configured and has access to the cluster.

