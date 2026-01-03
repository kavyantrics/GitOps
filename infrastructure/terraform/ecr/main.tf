# Amazon ECR Configuration
# Container registry for Docker images

terraform {
  required_version = ">= 1.0"
  
  backend "s3" {
    # Configure remote state backend
    # bucket = "your-terraform-state-bucket"
    # key    = "ecr/terraform.tfstate"
    # region = "us-east-1"
  }
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "repository_name" {
  description = "ECR repository name"
  type        = string
  default     = "gitops-app"
}

# Add ECR repository resources here
# This is a skeleton structure

