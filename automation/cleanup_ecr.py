#!/usr/bin/env python3
"""
Cleanup unused ECR images
Removes images older than specified days and keeps only N latest images
"""

import boto3
import sys
from datetime import datetime, timedelta
from typing import List, Dict

def get_ecr_client(region: str = 'us-east-1'):
    """Initialize ECR client"""
    return boto3.client('ecr', region_name=region)

def list_images(ecr_client, repository_name: str) -> List[Dict]:
    """List all images in ECR repository"""
    try:
        paginator = ecr_client.get_paginator('list_images')
        images = []
        for page in paginator.paginate(repositoryName=repository_name):
            images.extend(page.get('imageIds', []))
        return images
    except Exception as e:
        print(f"Error listing images: {e}")
        sys.exit(1)

def get_image_details(ecr_client, repository_name: str, image_ids: List[Dict]) -> List[Dict]:
    """Get detailed information about images including push date"""
    try:
        response = ecr_client.batch_get_image(
            repositoryName=repository_name,
            imageIds=image_ids
        )
        return response.get('images', [])
    except Exception as e:
        print(f"Error getting image details: {e}")
        return []

def cleanup_old_images(
    repository_name: str,
    days_to_keep: int = 30,
    keep_latest: int = 10,
    region: str = 'us-east-1',
    dry_run: bool = True
):
    """
    Cleanup old ECR images
    
    Args:
        repository_name: ECR repository name
        days_to_keep: Keep images newer than this many days
        keep_latest: Always keep this many latest images
        region: AWS region
        dry_run: If True, only show what would be deleted
    """
    ecr_client = get_ecr_client(region)
    
    print(f"Scanning repository: {repository_name}")
    image_ids = list_images(ecr_client, repository_name)
    print(f"Found {len(image_ids)} images")
    
    if not image_ids:
        print("No images to process")
        return
    
    # Get image details
    image_details = get_image_details(ecr_client, repository_name, image_ids)
    
    # Sort by push date (newest first)
    image_details.sort(key=lambda x: x.get('imagePushedAt', datetime.min), reverse=True)
    
    # Keep latest N images
    images_to_keep = image_details[:keep_latest]
    images_to_check = image_details[keep_latest:]
    
    cutoff_date = datetime.now(datetime.now().astimezone().tzinfo) - timedelta(days=days_to_keep)
    
    images_to_delete = []
    for image in images_to_check:
        pushed_at = image.get('imagePushedAt')
        if pushed_at and pushed_at < cutoff_date:
            images_to_delete.append(image)
    
    print(f"\nImages to keep (latest {keep_latest}): {len(images_to_keep)}")
    print(f"Images to delete (older than {days_to_keep} days): {len(images_to_delete)}")
    
    if images_to_delete:
        image_ids_to_delete = [
            {'imageDigest': img['imageId']['imageDigest']}
            for img in images_to_delete
            if 'imageDigest' in img.get('imageId', {})
        ]
        
        if dry_run:
            print("\n[DRY RUN] Would delete:")
            for img in images_to_delete[:5]:  # Show first 5
                print(f"  - {img.get('imageId', {}).get('imageTag', 'untagged')}")
            if len(images_to_delete) > 5:
                print(f"  ... and {len(images_to_delete) - 5} more")
        else:
            try:
                ecr_client.batch_delete_image(
                    repositoryName=repository_name,
                    imageIds=image_ids_to_delete
                )
                print(f"\nSuccessfully deleted {len(images_to_delete)} images")
            except Exception as e:
                print(f"Error deleting images: {e}")
                sys.exit(1)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Cleanup old ECR images')
    parser.add_argument('--repository', required=True, help='ECR repository name')
    parser.add_argument('--days', type=int, default=30, help='Days to keep images (default: 30)')
    parser.add_argument('--keep-latest', type=int, default=10, help='Always keep N latest images (default: 10)')
    parser.add_argument('--region', default='us-east-1', help='AWS region (default: us-east-1)')
    parser.add_argument('--execute', action='store_true', help='Actually delete images (default: dry run)')
    
    args = parser.parse_args()
    
    cleanup_old_images(
        repository_name=args.repository,
        days_to_keep=args.days,
        keep_latest=args.keep_latest,
        region=args.region,
        dry_run=not args.execute
    )

