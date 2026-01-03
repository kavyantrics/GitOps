# Terraform Infrastructure

This directory contains Terraform modules for provisioning AWS infrastructure.

## Structure

```
terraform/
├── vpc/          # VPC, subnets, internet gateway
├── eks/          # Amazon EKS cluster
├── ecr/          # Container registry
└── iam/          # IAM roles and policies
```

## Usage

1. Configure remote state backend in each module's `main.tf`
2. Initialize Terraform: `terraform init`
3. Plan changes: `terraform plan`
4. Apply: `terraform apply`

## Remote State

Configure S3 backend for state management:
- S3 bucket for state storage
- DynamoDB table for state locking

## Order of Deployment

1. VPC
2. IAM
3. ECR
4. EKS (depends on VPC and IAM)

