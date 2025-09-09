#!/usr/bin/env bash
set -euo pipefail

minikube start --cpus=4 --memory=6g
minikube addons enable ingress

# Install Argo CD
kubectl create namespace argocd || true
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
helm install argocd argo/argo-cd -n argocd --set server.service.type=ClusterIP

# Install Prometheus Stack
kubectl create namespace monitoring || true
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install kube-prom-stack prometheus-community/kube-prometheus-stack -n monitoring
echo "Done. Port-forward ArgoCD: kubectl -n argocd port-forward svc/argocd-server 8080:80"
