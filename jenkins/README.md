# Jenkins Configuration

This directory contains Jenkins pipeline configurations for the GitOps platform.

## Jenkinsfile

The `Jenkinsfile` defines a CI/CD pipeline that:
1. Checks out code
2. Runs tests
3. Builds Docker image
4. Pushes to Amazon ECR
5. Updates GitOps manifests

## Setup

1. Install Jenkins on EC2 (t3.medium instance)
2. Install required plugins:
   - AWS Steps
   - Docker Pipeline
   - Git
   - GitHub Integration
3. Configure AWS credentials in Jenkins
4. Create a new pipeline job and point to this Jenkinsfile

## Usage

The pipeline can be triggered:
- Manually from Jenkins UI
- Via webhook from GitHub
- On schedule (cron)

## Differences from GitHub Actions

Jenkins provides:
- Legacy enterprise CI/CD support
- More granular control over pipeline stages
- Integration with on-premise systems
- Custom plugins ecosystem

