#!/bin/bash
# =============================================================================
#  2026 - Deployment Script (AKS)
# =============================================================================
# This script deploys all Kubernetes resources in the correct order

set -e

echo "=========================================="
echo " 2026 - Kubernetes Deployment Script"
echo "=========================================="

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "ERROR: kubectl is not configured. Please configure your AKS cluster connection."
    echo "Run: az aks get-credentials --resource-group <RESOURCE_GROUP> -ame <AKS_CLUSTER_NAME>"
    exit 1
fi


echo ""
echo "Step 1: Creating ConfigMap..."
kubectl apply -f k8s/01-configmap.yaml

echo ""
echo "Step 2: Creating Secrets..."
kubectl apply -f k8s/02-secrets.yaml

echo ""
echo "Step 3: Creating Persistent Volume Claim..."
kubectl apply -f k8s/03-postgres-pvc.yaml

echo ""
echo "Step 4: Deploying PostgreSQL Database..."
kubectl apply -f k8s/04-postgres-statefulset.yaml
kubectl apply -f k8s/05-postgres-service.yaml

echo ""
echo "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres

echo ""
echo "Step 5: Deploying Service API..."
kubectl apply -f k8s/06-service-api-deployment.yaml
kubectl apply -f k8s/07-service-api-service.yaml

echo ""
echo "Waiting for Service API pods to be ready..."
kubectl wait --for=condition=ready pod -l app=service-api

echo ""
echo "Step 6: Creating Horizontal Pod Autoscaler..."
kubectl apply -f k8s/08-hpa.yaml

echo ""
echo "Step 7: Creating Ingress..."
kubectl apply -f k8s/09-ingress.yaml

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Getting deployment status..."
kubectl get all  
echo ""
echo "Getting Ingress status..."
kubectl get ingress  
echo ""
echo "NOTE: It may take a few minutes for the NGINX external IP to be assigned."
echo "Run: kubectl get svc  ingressginx ingressginx-controller"
echo ""
