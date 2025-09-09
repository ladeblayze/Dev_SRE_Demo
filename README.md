# DevOps/SRE Demo: Minikube + Argo CD + GitHub Actions + Prometheus

A free, laptop-friendly replica of a typical DevOps/SRE workflow:
- **Minikube** stands in for AWS EKS.
- **Argo CD** handles GitOps-style continuous delivery.
- **GitHub Actions** builds & (optionally) pushes your Docker image to GHCR.
- **Prometheus + Grafana** (via `kube-prometheus-stack`) provide observability (Datadog substitute).

> Time: ~60–90 minutes on a typical laptop (8GB+ RAM recommended).

---

## 0) Prerequisites

- Docker Desktop (or Docker Engine)
- kubectl
- Helm
- Minikube
- Git + GitHub account
- (Optional) GHCR push: a GitHub Personal Access Token with `write:packages`

---

## 1) Start Minikube

**Linux/macOS (bash):**
```bash
minikube start --cpus=4 --memory=6g
minikube addons enable ingress
```

**Windows (PowerShell):**
```powershell
minikube start --cpus=4 --memory=6g
minikube addons enable ingress
```

Verify:
```bash
kubectl get nodes
kubectl get pods -A
```

---

## 2) Build the app image

This repo includes a tiny Flask app with `/` and `/healthz`.

**Option A — Local-only (fastest for Minikube):**
```bash
# Point Docker to Minikube's Docker daemon so the cluster can pull images without a registry
eval $(minikube -p minikube docker-env)   # PowerShell: & minikube -p minikube docker-env | Invoke-Expression
docker build -t demo/app:local ./app
```

**Option B — Push to GHCR (for CI):**
1. Create `Packages: write` PAT at https://github.com/settings/tokens
2. Login locally (optional):  
   ```bash
   echo $GH_PAT | docker login ghcr.io -u <your-gh-username> --password-stdin
   docker build -t ghcr.io/<your-gh-username>/demo-app:latest ./app
   docker push ghcr.io/<your-gh-username>/demo-app:latest
   ```

---

## 3) Install Argo CD

```bash
kubectl create namespace argocd
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
helm install argocd argo/argo-cd -n argocd --set server.service.type=ClusterIP
kubectl -n argocd rollout status deploy/argocd-server
```

Port-forward the UI:
```bash
kubectl -n argocd port-forward svc/argocd-server 8080:80
```
Open http://localhost:8080

Get the admin password:
```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{{.data.password}}" | base64 -d; echo
```

---

## 4) Deploy the app with Argo CD (GitOps)

Commit this repo to GitHub. Then in Argo CD UI:
- **New App** → Name: `demo-app`
- **Project:** default
- **Sync policy:** Automatic (optional)
- **Repository URL:** your GitHub repo (public is easiest)
- **Path:** `helm/app`
- **Cluster URL:** https://kubernetes.default.svc
- **Namespace:** `demo` (Argo will create it)

Or apply the manifest (edit `repoURL` to your fork):
```bash
kubectl create ns demo
kubectl apply -f k8s/argocd/app.yaml
```

If you used **local build (demo/app:local)**, ensure Helm values use `demo/app:local`.  
If you used **GHCR**, set the image to `ghcr.io/<your-user>/demo-app:latest`.

Check rollout:
```bash
kubectl -n demo get deploy,po,svc
kubectl -n demo port-forward svc/demo-app 8081:80
curl http://localhost:8081
```

---

## 5) Add Observability (Prometheus + Grafana)

```bash
kubectl create ns monitoring
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install kube-prom-stack prometheus-community/kube-prometheus-stack -n monitoring
kubectl -n monitoring rollout status deploy/kube-prom-stack-grafana
```

Access Grafana:
```bash
kubectl -n monitoring port-forward svc/kube-prom-stack-grafana 3000:80
```
Open http://localhost:3000 (user: `admin`, password: get via:)
```bash
kubectl -n monitoring get secret kube-prom-stack-grafana -o jsonpath="{{.data.admin-password}}" | base64 -d; echo
```

Our Helm chart ships a `ServiceMonitor` so your app metrics (`/metrics`) are scraped automatically.

---

## 6) CI with GitHub Actions

The workflow **builds** your image on every PR and **pushes** on merge to `main` (if you set the secret).

- Create repo secrets:
  - `GHCR_USERNAME` = your GitHub username
  - `GHCR_TOKEN` = PAT with `write:packages`

Push your repo; Actions should run automatically.  
You can see logs in **GitHub → Actions**.

---

## 7) Simple Incident Drill

1. Generate traffic & errors:
   ```bash
   # Send 200 requests, 10% will intentionally fail
   for i in $(seq 1 200); do curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8081/; sleep 0.05; done
   ```
2. In Grafana, use **Kubernetes/Compute Resources/Pods** and **Prometheus/HTTP Overview** (or build your own) to watch:
   - `http_requests_total`
   - `http_request_duration_seconds_bucket`
   - `demo_errors_total`
3. Triage:
   - `kubectl -n demo logs deploy/demo-app`
   - `kubectl -n demo describe deploy demo-app`
   - Roll back in Argo CD UI (**HISTORY & ROLLBACK**).

---

## 8) Teardown

```bash
helm -n monitoring uninstall kube-prom-stack
helm -n argocd uninstall argocd
kubectl delete ns monitoring demo argocd
minikube delete
```

---

## What you learned
- GitOps flow (Git → Argo CD → Cluster)
- CI with GitHub Actions
- Containerized app on Kubernetes with Helm
- Basic monitoring with Prometheus/Grafana
- Incident triage and rollback
