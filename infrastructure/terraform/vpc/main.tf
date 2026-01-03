# VPC Configuration
# This module creates a VPC with public and private subnets for the GitOps platform

terraform {
  required_version = ">= 1.0"
  
  backend "s3" {
    # Configure remote state backend
    # bucket = "your-terraform-state-bucket"
    # key    = "vpc/terraform.tfstate"
    # region = "us-east-1"
  }
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "gitops-platform"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

# Add your VPC resources here
# This is a skeleton structure

