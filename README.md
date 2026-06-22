# NAGP 2026 - Kubernetes, DevOps & FinOps Assignment

## Multi-tier Architecture on Kubernetes (AKS)

This project implements a multi-tier architecture consisting of a Python Flask API service and PostgreSQL database, deployed on Azure Kubernetes Service (AKS).

---

## Table of Contents

- [Project Overview](#project-overview)
- [Links](#links)
- [Architecture](#architecture)
- [Requirements Mapping](#requirements-mapping)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Deployment Guide](#detailed-deployment-guide)
- [API Endpoints](#api-endpoints)
- [Demonstration](#demonstration)
- [FinOps Considerations](#finops-considerations)

---

## Links

| Resource | URL |
|----------|-----|
| **Code Repository** | `https://github.com/ChSChaitanya/nagp_k8s` |
| **Docker Hub Image** | `https://hub.docker.com/repository/docker/y6bt250/nagp-service-api` |
| **Service API URL** | `http://40.91.80.6/api/employees` |

---

## Architecture

```
                    ┌─────────────────────────────────────────────────────────────┐
                    │                         AKS Cluster                          │
                    │                                                              │
   Internet         │   ┌───────────┐    ┌─────────────────────────────────────┐  │
      │             │   │           │    │         Service API Tier            │  │
      │             │   │  Ingress  │    │  ┌─────────┐  ┌─────────┐           │  │
      └─────────────┼──►│ (NGINX)   │───►│  │ Pod 1   │  │ Pod 2   │           │  │
                    │   │           │    │  │ Flask   │  │ Flask   │           │  │
                    │   └───────────┘    │  └─────────┘  └─────────┘           │  │
                    │                    │  ┌─────────┐  ┌─────────┐           │  │
                    │                    │  │ Pod 3   │  │ Pod 4   │           │  │
                    │                    │  │ Flask   │  │ Flask   │           │  │
                    │                    │  └─────────┘  └─────────┘           │  │
                    │                    │         │ HPA enabled               │  │
                    │                    └─────────┼───────────────────────────┘  │
                    │                              │                              │
                    │                              │ ClusterIP Service            │
                    │                              ▼                              │
                    │   ┌─────────────────────────────────────────────────────┐   │
                    │   │               Database Tier                          │   │
                    │   │   ┌─────────────────────────────────────────────┐   │   │
                    │   │   │          PostgreSQL Deployment              │   │   │
                    │   │   │   ┌────────────┐    ┌──────────────────┐   │   │   │
                    │   │   │   │ PostgreSQL │───►│ Persistent Volume │   │   │   │
                    │   │   │   │   Pod      │    │      (1Gi)        │   │   │   │
                    │   │   │   └────────────┘    └──────────────────┘   │   │   │
                    │   │   └─────────────────────────────────────────────┘   │   │
                    │   │              NOT exposed externally                  │   │
                    │   └─────────────────────────────────────────────────────┘   │
                    │                                                              │
                    │   ┌──────────────────┐  ┌──────────────────┐                │
                    │   │    ConfigMap     │  │     Secrets      │                │
                    │   │  (DB Settings)   │  │  (DB Password)   │                │
                    │   └──────────────────┘  └──────────────────┘                │
                    │                                                              │
                    └──────────────────────────────────────────────────────────────┘
```

---

### Kubernetes Requirements

| Feature | Service API Tier | Database Tier | Implementation |
|---------|-----------------|---------------|----------------|
| Exposed outside cluster |  Yes |  No | Ingress (NGINX) for API, ClusterIP for DB |
| Number of pods | 4 | 1 | Deployment replicas: 4, Deployment replicas: 1 |
| Rolling updates |  Yes |  No | RollingUpdate strategy on Deployment |
| Persistent storage |  No |  Yes | PVC with AKS `managed-csi` StorageClass |
| ConfigMap |  Yes | Optional | DB connection settings via ConfigMap |
| Secrets |  Yes |  Yes | DB passwords in base64-encoded Secret |

### Other Requirements

| Requirement | Implementation |
|-------------|----------------|
| DB config outside pod/code | ConfigMap (`db-config`) with environment variables |
| Password not visible in YAML | Kubernetes Secrets with base64 encoding |
| Data persistence | PVC attached to PostgreSQL Deployment |
| No Pod IPs for communication | Service DNS names (`postgres-service`) |
| External access via Ingress | NGINX Ingress Controller |
| Self-healing | Liveness/Readiness probes |
| HPA on Service API | CPU/Memory based scaling (4-10 pods) |

---

##  Prerequisites

1. **Azure CLI** installed and logged in
2. **kubectl** installed
3. **Docker** installed and running
4. **AKS Cluster** created
5. **Docker Hub account** for pushing images
6. **Shell**: use PowerShell for `kubectl` commands; use **Git Bash** or **WSL** to run scripts in `scripts/` (they are bash scripts)
7. *(Optional)* `jq` for pretty-printing API JSON responses

### Azure CLI Setup

```bash
# login to your azure accounr
az login
# set the cluster subscription
az account set --subscription < YOUR AZURE SUBSCRIPTION >
# Get credentials for your AKS cluster
az aks get-credentials --resource-group <RESOURCE_GROUP> --name <AKS_CLUSTER_NAME>
```

### Install NGINX Ingress Controller (AKS)

If you don’t already have an ingress controller installed, install `ingress-nginx`:

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx
```

Get the external IP for NGINX:

```bash
kubectl get svc ingress-nginx-controller -w
```

### Metrics for HPA (AKS)

HPA needs metrics. If `kubectl top pods` fails, install metrics-server:

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

Validate:

```bash
kubectl top nodes
kubectl top pods
```

### (Optional) Create/rotate DB Secret without editing YAML

```bash
kubectl create secret generic db-secret \
  --from-literal=DB_PASSWORD='<PASSWORD>' \
  --from-literal=POSTGRES_PASSWORD='<PASSWORD>' \
  --from-literal=POSTGRES_USER='nagpuser' \
  --from-literal=POSTGRES_DB='nagpdb' \
  --dry-run=client -o yaml | kubectl apply -f -
```

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/y6bt250/nagp_k8s.git
cd nagp_k8s
```

### 2. Build and Push Docker Image

```bash
# Update Docker Hub username in scripts/build-push.sh
# Then run:
cd service-api
docker build -t YOUR_DOCKERHUB_USERNAME/nagp-service-api:latest .
docker push YOUR_DOCKERHUB_USERNAME/nagp-service-api:latest
```

### 3. Update Kubernetes Manifests

Edit `k8s/06-service-api-deployment.yaml` and replace:
```yaml
image: YOUR_DOCKERHUB_USERNAME/nagp-service-api:latest
```

### 4. Deploy to AKS

```bash
# Apply all manifests
kubectl apply -f k8s/
```

### 5. Verify Deployment

```bash
# Check all resources
kubectl get all

# Get NGINX external IP (may take a few minutes)
kubectl get svc ingress-nginx-controller
```

---

##  Detailed Deployment Guide

### Step-by-Step Deployment

```bash

# 1. Create ConfigMap (database configuration)
kubectl apply -f k8s/01-configmap.yaml

# 2. Create Secrets (database password)
kubectl apply -f k8s/02-secrets.yaml

# 3. Create PVC for database persistence
kubectl apply -f k8s/03-postgres-pvc.yaml

# 4. Deploy PostgreSQL
kubectl apply -f k8s/04-postgres-statefulset.yaml
kubectl apply -f k8s/05-postgres-service.yaml

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgres

# 5. Deploy Service API
kubectl apply -f k8s/06-service-api-deployment.yaml
kubectl apply -f k8s/07-service-api-service.yaml

# 6. Create HPA
kubectl apply -f k8s/08-hpa.yaml

# 7. Create Ingress
kubectl apply -f k8s/09-ingress.yaml
```

### Get External IP

```bash
# Wait for the NGINX external IP (may take a few minutes)
kubectl get svc ingress-nginx-controller -w
```

---

##  API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and available endpoints |
| `/health` | GET | Health check endpoint |
| `/ready` | GET | Readiness check endpoint (verifies DB connection) |
| `/api/employees` | GET | Fetch all employees from database |
| `/api/employees/<id>` | GET | Fetch specific employee by ID |
| `/api/info` | GET | Pod and environment information |

### Example API Calls

```bash
# Get API info
curl http://<NGINX_EXTERNAL_IP>/

# Health check
curl http://<NGINX_EXTERNAL_IP>/health

# Get all employees
curl http://<NGINX_EXTERNAL_IP>/api/employees

# Get specific employee
curl http://<NGINX_EXTERNAL_IP>/api/employees/1

# Get pod info
curl http://<NGINX_EXTERNAL_IP>/api/info
```

## FinOps Considerations

### Resource Requests and Limits

| Component | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|-------------|-----------|----------------|--------------|
| Service API | 100m | 500m | 128Mi | 256Mi |
| PostgreSQL | 100m | 500m | 256Mi | 512Mi |

### Cost Optimization Opportunities

1. **Right-sizing Resources**
   - Monitor actual CPU/memory usage with `kubectl top pods`
   - Adjust requests/limits based on observed metrics
   - Current settings are conservative starting points

2. **HPA Configuration**
   - Minimum 4 replicas ensures availability
   - Maximum 10 replicas prevents runaway scaling
   - Scale-down stabilization (5 min) prevents unnecessary pod churn

3. **Use Preemptible/Spot Nodes**
   ```bash
   # Example : create an AKS spot node pool
   # az aks nodepool add --resource-group <RG> --cluster-name <AKS> --name spotpool --priority Spot --eviction-policy Delete --spot-max-price -1 --node-count 1 --node-vm-size <VM_SIZE>
   ```

4. **Resource Quotas**
   ```yaml
   # Apply namespace resource quotas
   apiVersion: v1
   kind: ResourceQuota
   metadata:
     name: nagp-quota
     namespace: nagp
   spec:
     hard:
       requests.cpu: "2"
       requests.memory: 2Gi
       limits.cpu: "4"
       limits.memory: 4Gi
   ```

5. **Cluster Autoscaler**
   - Enable/tune AKS cluster autoscaler on your node pool(s)
   - Automatically scales nodes based on pending pods (helps cost control)

6. **Pod Disruption Budget**
   - Ensures minimum availability during node maintenance
   - Reduces over-provisioning for high availability

---

## Project Structure

```
nagp/
├── service-api/                 # Python Flask application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration from env vars
│   │   ├── database.py         # Connection pooling
│   │   ├── main.py             # Flask app factory
│   │   └── routes.py           # API endpoints
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── requirements.txt
│   └── run.py
├── k8s/                        # Kubernetes manifests
│   ├── 01-configmap.yaml
│   ├── 02-secrets.yaml
│   ├── 03-postgres-pvc.yaml
│   ├── 04-postgres-statefulset.yaml
│   ├── 05-postgres-service.yaml
│   ├── 06-service-api-deployment.yaml
│   ├── 07-service-api-service.yaml
│   ├── 08-hpa.yaml
│   └── 09-ingress.yaml
├── scripts/                    # Helper scripts
│   ├── deploy.sh
│   ├── build-push.sh
│   └── demo.sh
├── docs/                       # Documentation
│   └── ASSIGNMENT_DOCUMENTATION.pdf
└── README.md
```

---

## Cleanup

To delete all resources and avoid additional costs:
delete AKS cluster entirely
# az aks delete --resource-group <RESOURCE_GROUP> --name <AKS_CLUSTER_NAME> --yes --no-wait
```

---

## Notes

- Replace `YOUR_DOCKERHUB_USERNAME` with your actual Docker Hub username
- Replace `YOUR_USERNAME` with your GitHub username
- NGINX external IP provisioning may take a few minutes on AKS
- For security, do not print database passwords in docs or YAML comments

---

## Author: Srinivasa Chaitanya Chaganty

NAGP 2026 - Technology Band III Batch

---
