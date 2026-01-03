# EKS Cluster Configuration
# Production Kubernetes cluster using Amazon EKS

terraform {
  required_version = ">= 1.0"
  
  backend "s3" {
    # Configure remote state backend
    # bucket = "your-terraform-state-bucket"
    # key    = "eks/terraform.tfstate"
    # region = "us-east-1"
  }
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "gitops-eks-prod"
}

variable "vpc_id" {
  description = "VPC ID where EKS will be deployed"
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs for EKS"
  type        = list(string)
}

# Add EKS cluster resources here
# This is a skeleton structure

