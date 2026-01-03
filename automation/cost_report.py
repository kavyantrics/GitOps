#!/usr/bin/env python3
"""
Generate AWS cost report for GitOps platform resources
"""

import boto3
from datetime import datetime, timedelta
from typing import Dict, List

def get_cost_explorer_client():
    """Initialize AWS Cost Explorer client"""
    return boto3.client('ce')

def get_ec2_costs(ce_client, start_date: str, end_date: str) -> Dict:
    """Get EC2 instance costs"""
    response = ce_client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='DAILY',
        Metrics=['BlendedCost'],
        Filter={
            'Dimensions': {
                'Key': 'SERVICE',
                'Values': ['Amazon Elastic Compute Cloud - Compute']
            }
        },
        GroupBy=[
            {'Type': 'DIMENSION', 'Key': 'INSTANCE_TYPE'}
        ]
    )
    return response

def get_eks_costs(ce_client, start_date: str, end_date: str) -> Dict:
    """Get EKS cluster costs"""
    response = ce_client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='DAILY',
        Metrics=['BlendedCost'],
        Filter={
            'Dimensions': {
                'Key': 'SERVICE',
                'Values': ['Amazon Elastic Container Service for Kubernetes']
            }
        }
    )
    return response

def get_ecr_costs(ce_client, start_date: str, end_date: str) -> Dict:
    """Get ECR storage costs"""
    response = ce_client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='DAILY',
        Metrics=['BlendedCost'],
        Filter={
            'Dimensions': {
                'Key': 'SERVICE',
                'Values': ['Amazon EC2 Container Registry (ECR)']
            }
        }
    )
    return response

def generate_cost_report(days: int = 30):
    """
    Generate cost report for the last N days
    
    Args:
        days: Number of days to report on
    """
    ce_client = get_cost_explorer_client()
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    print(f"Cost Report: {start_date} to {end_date}\n")
    print("=" * 60)
    
    # EC2 Costs
    print("\nEC2 Instance Costs:")
    print("-" * 60)
    try:
        ec2_costs = get_ec2_costs(ce_client, start_date, end_date)
        for result in ec2_costs.get('ResultsByTime', []):
            for group in result.get('Groups', []):
                instance_type = group.get('Keys', ['Unknown'])[0]
                cost = group.get('Metrics', {}).get('BlendedCost', {}).get('Amount', '0')
                print(f"  {instance_type}: ${float(cost):.2f}")
    except Exception as e:
        print(f"  Error retrieving EC2 costs: {e}")
    
    # EKS Costs
    print("\nEKS Cluster Costs:")
    print("-" * 60)
    try:
        eks_costs = get_eks_costs(ce_client, start_date, end_date)
        total_eks = 0
        for result in eks_costs.get('ResultsByTime', []):
            cost = float(result.get('Total', {}).get('BlendedCost', {}).get('Amount', '0'))
            total_eks += cost
        print(f"  Total EKS: ${total_eks:.2f}")
    except Exception as e:
        print(f"  Error retrieving EKS costs: {e}")
    
    # ECR Costs
    print("\nECR Storage Costs:")
    print("-" * 60)
    try:
        ecr_costs = get_ecr_costs(ce_client, start_date, end_date)
        total_ecr = 0
        for result in ecr_costs.get('ResultsByTime', []):
            cost = float(result.get('Total', {}).get('BlendedCost', {}).get('Amount', '0'))
            total_ecr += cost
        print(f"  Total ECR: ${total_ecr:.2f}")
    except Exception as e:
        print(f"  Error retrieving ECR costs: {e}")
    
    print("\n" + "=" * 60)
    print("Note: Cost data may take up to 24 hours to appear")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate AWS cost report')
    parser.add_argument('--days', type=int, default=30, help='Number of days to report (default: 30)')
    
    args = parser.parse_args()
    generate_cost_report(args.days)

