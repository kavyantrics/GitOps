# VPC Outputs
# Export VPC IDs, subnet IDs, etc. for use in other modules

output "vpc_id" {
  description = "VPC ID"
  value       = ""
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = []
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = []
}

