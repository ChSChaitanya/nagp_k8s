#!/bin/bash
# =============================================================================
# NAGP 2026 - Docker Build and Push Script
# =============================================================================

set -e

# Configuration - REPLACE THESE VALUES
DOCKER_HUB_USERNAME="YOUR_DOCKERHUB_USERNAME"
IMAGE_NAME="nagp-service-api"
TAG="${1:-latest}"

echo "=========================================="
echo "NAGP 2026 - Docker Build & Push Script"
echo "=========================================="

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "ERROR: Docker is not running. Please start Docker."
    exit 1
fi

cd service-api

echo ""
echo "Step 1: Building Docker image..."
docker build -t ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${TAG} .

echo ""
echo "Step 2: Tagging as latest..."
docker tag ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${TAG} ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:latest

echo ""
echo "Step 3: Pushing to Docker Hub..."
docker push ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${TAG}
docker push ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:latest

echo ""
echo "=========================================="
echo "Build and Push Complete!"
echo "=========================================="
echo ""
echo "Image: ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${TAG}"
echo "Image: ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:latest"
echo ""
echo "Don't forget to update the image in k8s/06-service-api-deployment.yaml"
