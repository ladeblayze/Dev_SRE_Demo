# DevOps/SRE Demo: Minikube + Argo CD + GitHub Actions + Prometheus  

This project demonstrates a laptop-friendly, end-to-end DevOps/SRE workflow that replicates a modern cloud-native environment. It integrates container orchestration, GitOps delivery, CI/CD pipelines, and observability.  

### Stack Overview
- **Minikube** → Local Kubernetes cluster (EKS substitute)  
- **Argo CD** → GitOps-style continuous delivery  
- **GitHub Actions** → CI pipeline for image builds and GHCR pushes  
- **Prometheus + Grafana** → Observability and monitoring (Datadog substitute)  
- **Flask App** → Sample application with `/` and `/healthz` endpoints  

---

## Project Flow

### 1. Cluster Setup  
- Provisioned a local Kubernetes cluster with **Minikube** (4 CPUs, 6 GB RAM).  
- Enabled ingress for service routing.  
- Verified cluster readiness with `kubectl get nodes` and `kubectl get pods -A`.  

### 2. Application Build  
- Built and containerized a lightweight Flask application.  
- Supported two workflows:  
  - **Local build** (directly accessible to Minikube)  
  - **Remote push** to **GitHub Container Registry (GHCR)** using a Personal Access Token.  

### 3. Continuous Delivery with Argo CD  
- Installed Argo CD via Helm in a dedicated namespace.  
- Configured a GitOps pipeline that syncs application manifests from GitHub.  
- Deployed the Flask app automatically on cluster changes.  
- Verified rollout with `kubectl get deploy,po,svc`.  

### 4. Observability Stack  
- Installed **kube-prometheus-stack** (Prometheus + Grafana).  
- Configured metrics scraping with built-in ServiceMonitor for `/metrics`.  
- Enabled dashboards for application and cluster health monitoring.  
- Example metrics tracked:  
  - `http_requests_total`  
  - `http_request_duration_seconds_bucket`  
  - `demo_errors_total`  

### 5. CI Pipeline with GitHub Actions  
- Configured workflows to:  
  - Build Docker images for every pull request.  
  - Push production images to GHCR on merge to `main`.  
- Secured with repo secrets:  
  - `GHCR_USERNAME`  
  - `GHCR_TOKEN`  

### 6. Incident Drill  
- Simulated traffic with mixed success/failure responses.  
- Used Grafana dashboards to monitor error rates and latency.  
- Investigated logs via `kubectl logs` and deployment status via `kubectl describe`.  
- Rolled back faulty deployments through Argo CD’s rollback functionality.  

### 7. Teardown  
- Removed monitoring and GitOps components with Helm uninstall.  
- Deleted namespaces and Minikube cluster to clean up the environment.  

---

## Key Takeaways
- Demonstrated **GitOps workflow** with Argo CD.  
- Built a **CI/CD pipeline** from source → container → deployment.  
- Integrated **observability** using Prometheus & Grafana.  
- Practiced **incident response** with monitoring, debugging, and rollback.  
- Delivered a **portable, end-to-end DevOps environment** on a local laptop.  
