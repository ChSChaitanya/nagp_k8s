#!/bin/bash
# =============================================================================
# NAGP 2026 - Demonstration Script
# =============================================================================
# This script demonstrates self-healing and other features

set -e

echo "=========================================="
echo "NAGP 2026 - Feature Demonstration Script"
echo "=========================================="

echo ""
echo "===== 1. Showing all deployed objects ====="
kubectl get all 
echo ""
kubectl get pvc 
echo ""
kubectl get hpa 
echo ""
kubectl get ingress 

echo ""
echo "===== 2. Testing API endpoint ====="
NGINX_EXTERNAL_IP=$(kubectl get svc ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
if [ -n "$NGINX_EXTERNAL_IP" ]; then
    echo "NGINX External IP: $NGINX_EXTERNAL_IP"
    echo ""
    echo "Testing /health endpoint:"
    curl -s http://${NGINX_EXTERNAL_IP}/health | jq .
    echo ""
    echo "Testing /api/employees endpoint:"
    curl -s http://${NGINX_EXTERNAL_IP}/api/employees | jq .
else
    echo "NGINX external IP not yet available. Try again in a few minutes."
fi

echo ""
echo "===== 3. Self-healing demonstration - API Pod ====="
echo "Current API pods:"
kubectl get pods -l app=service-api 
echo ""
echo "Killing one API pod..."
POD_NAME=$(kubectl get pods -l app=service-api  -o jsonpath='{.items[0].metadata.name}')
kubectl delete pod $POD_NAME 
echo ""
echo "Watching pods regenerate (wait 30 seconds)..."
sleep 5
kubectl get pods -l app=service-api  -w  || true
echo ""
echo "Final state of API pods:"
kubectl get pods -l app=service-api 

echo ""
echo "===== 4. Self-healing demonstration - Database Pod ====="
echo "Current Database pods:"
kubectl get pods -l app=postgres 
echo ""
echo "Killing database pod..."
kubectl delete pod -l app=postgres 
echo ""
echo "Watching pod regenerate (wait 60 seconds)..."
sleep 5
kubectl get pods -l app=postgres  -w || true
echo ""
echo "Final state of Database pods:"
kubectl get pods -l app=postgres 

echo ""
echo "===== 5. Verifying data persistence ====="
echo "Testing /api/employees endpoint after database restart:"
sleep 10
if [ -n "$NGINX_EXTERNAL_IP" ]; then
    curl -s http://${NGINX_EXTERNAL_IP}/api/employees | jq .
fi

echo ""
echo "===== 6. HPA Status ====="
kubectl get hpa 

echo ""
echo "=========================================="
echo "Demonstration Complete!"
echo "=========================================="
