# 🌍 Wanderlust

> A production-grade, highly available microservices application deployed on AWS EKS using Infrastructure as Code (IaC) and GitOps principles.

📖 **[Read the full Project Documentation](./PROJECT_DOCUMENTATION.md)** — architecture, API reference, Terraform/Ansible/Kubernetes deep-dives, CI/CD & GitOps pipelines, and security practices.

![Kubernetes](https://img.shields.io/badge/kubernetes-%23326ce5.svg?style=for-the-badge&logo=kubernetes&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Terraform](https://img.shields.io/badge/terraform-%235835CC.svg?style=for-the-badge&logo=terraform&logoColor=white)
![Ansible](https://img.shields.io/badge/ansible-%23EE0000.svg?style=for-the-badge&logo=ansible&logoColor=white)
![ArgoCD](https://img.shields.io/badge/Argo%20CD-EF7B4D?style=for-the-badge&logo=argo&logoColor=white)

---

## 📋 Table of Contents
- [Architecture Overview](#-architecture-overview)
- [Repository Structure](#-repository-structure)
- [Prerequisites](#-prerequisites)
- [Getting Started](#-getting-started)
  - [1. Infrastructure Provisioning (Terraform)](#1-infrastructure-provisioning-terraform)
  - [2. Server Configuration (Ansible)](#2-server-configuration-ansible)
  - [3. GitOps Deployment (ArgoCD)](#3-gitops-deployment-argocd)
- [Environment Variables & Secrets](#-environment-variables--secrets)
- [Live Endpoints](#-live-endpoints)
- [License & Authors](#-license--authors)

---

## 🏗️ Architecture Overview

The Wanderlust platform is built with a GitOps pipeline ensuring security, isolation, and automated synchronization:

```text
[ Internet Users ]
       │
       ▼ (HTTPS)
[ Cloudflare DNS ]
       │
       ▼
[ AWS ALB / NGINX Ingress ]
       │
       ├─────────────────────────┐
       ▼                         ▼
[ Frontend App ]        [ Backend API Node.js ]
                                 │
                                 ▼
                     [ StatefulSet: MongoDB ]
