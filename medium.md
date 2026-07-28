<!-- ============================================================================
MEDIUM PUBLISHING CHECKLIST (delete this comment block before pasting)
----------------------------------------------------------------------------
TITLE    : I Typed One Command and a Whole Cloud Platform Built Itself
SUBTITLE : How I took a travel blog from git push to a self-healing, monitored
           Kubernetes platform on AWS — with Terraform, Ansible, Jenkins & ArgoCD
TAGS (5) : DevOps, Kubernetes, Terraform, GitOps, AWS
IMAGES   : Medium strips local image links — drag-and-drop each PNG from
           medium/images/ onto its marker. Alt text is included.
SEO      : Settings → SEO title: "Zero-Touch DevOps: Terraform, Ansible,
           Jenkins and ArgoCD on AWS" ; description = subtitle above.
CANONICAL: If you also post on your blog/dev.to, set Medium's canonical link.
============================================================================ -->

![Cover: a traveler overlooking a valley, the sky above filled with a holographic constellation of cloud infrastructure — containers, gears and network nodes](images/cover.png)
*Every side project starts with a dream. Mine was to never SSH into a server again.*

---

I typed one command, went to make coffee, and came back to a running cloud platform: a Kubernetes cluster wired to a CI server, a GitOps controller reconciling my deployments, Prometheus scraping metrics, Grafana dashboards glowing — and six DNS records published on Cloudflare. No console clicks. No SSH sessions. No snowflake servers.

That command was `terraform apply` — and this is the story of **Wanderlust**, the full-stack travel blog I built not to showcase a blog, but to prove an end-to-end, production-grade delivery platform: **Terraform → Ansible → Kubernetes → Jenkins → ArgoCD**, all living in one repository.

## Why another blogging app?

Everyone has built a CRUD blog. Recruiters have seen a hundred MERN clones. But here's the uncomfortable truth about most portfolio projects: they end at `npm start`. How does code get to production? Who rebuilds the server when it dies? Where do the secrets live? What happens at 3 a.m. when a pod crashes?

I wanted one project that answered all of those questions. Wanderlust is deliberately two projects in one trench coat:

1. **The application** — a React 18 + TypeScript SPA and an Express + TypeScript API with JWT cookie auth, Google OAuth, role-based access control, MongoDB persistence, and a Redis read-through cache.
2. **The platform** — the infrastructure, pipelines, and GitOps machinery that take that app from a `git push` to production without human hands.

The app is the passenger. The platform is the story.

## TL;DR — the pipeline in one breath

> One `terraform apply` provisions a custom AWS VPC, two EC2 servers, an SSH keypair, and all DNS records — then waits for SSH and hands off to Ansible, which installs tooling, stands up a Kubernetes cluster, and deploys ArgoCD plus a full monitoring stack. From then on, Jenkins builds immutable Docker images on every merge, and ArgoCD continuously syncs the cluster with the manifests in Git. Rollback is `git revert`.

## The architecture

![Architecture diagram: Users hit Cloudflare DNS (records created by Terraform), which routes into an AWS VPC containing a Jenkins CI server and a deployment server running a kind Kubernetes cluster. Inside: NGINX Ingress routes to the React frontend and Express backend, which talk to MongoDB and Redis, while ArgoCD and the Prometheus/Grafana monitoring stack run alongside. Git, shown at the bottom, is the single source of truth.](images/diagram-architecture.png)
*Everything you see here — including the diagram's existence in Git — is reproducible from the repository.*

A few design choices worth calling out:

- **Separation of duties.** One EC2 box runs Jenkins (CI). A second box runs the workload cluster (CD). The CI server builds and pushes images — but holds *zero* cluster credentials. Deploy rights live only inside the cluster, where ArgoCD watches Git.
- **Git is the control plane.** Application code, Terraform state layout, Ansible playbooks, *and* the Kubernetes desired state (`deployment/k8s_manifest/`) all live in version control. Manual `kubectl` edits aren't configuration — they're drift, and ArgoCD corrects them.
- **Immutable artifacts.** Every Jenkins build tags images `0.0.<BUILD_NUMBER>`. `:latest` moves forward, but every historical build is deployable forever.

## Zero-touch: watching infrastructure build itself

![Illustration: a finger presses a glowing Enter key on a terminal; a stream of light pours out and assembles a miniature city of servers, containers, clouds and gears by itself](images/zero-touch.png)
*The best ritual in DevOps: press Enter, walk away, come back to a platform.*

Here's the actual bootstrap chain, with no hidden manual steps:

1. **Terraform generates its own SSH keypair** (ED25519, via the `tls` provider) and writes the private key locally with `0600` permissions. No keys in the repo, ever.
2. It brings up the **networking layer**: a `10.0.0.0/16` VPC, internet gateway, public subnet, and two private subnets reserved for a future data tier.
3. It launches **two `t3.medium` instances** — the Jenkins server (bootstrapped via `user_data` with Docker + Jenkins) and the deployment server.
4. A `terraform_data` resource **polls the deployment server over SSH** until it answers — eliminating the classic "provisioner runs before SSH is ready" race condition.
5. Only then does Terraform trigger **six Ansible playbooks, in order**: base tools → kind cluster → NGINX ingress → MongoDB seed config → ArgoCD → the kube-prometheus stack.
6. Simultaneously, Terraform's Cloudflare provider **publishes six A-records** — `frontend.*`, `backend.*`, `argocd.*`, `prometheus.*`, `grafana.*`, `alertmanager.*` — all pointed at the deployment server and proxied through Cloudflare.

The Terraform state itself lives in an **encrypted S3 backend**, and the Ansible inventory file is *generated from live resource attributes* — no copy-pasting IPs.

```hcl
resource "cloudflare_dns_record" "argocd_dns_record" {
  zone_id = var.cloudflare_zone_id
  name    = "argocd.sujandongol.com.np"
  type    = "A"
  ttl     = 1
  content = aws_instance.deployment-server.public_ip
  proxied = true
}
```

*Six records like this, zero browser tabs opened in Cloudflare.*

## Commit → Image → Cluster

![Pipeline diagram with 8 numbered steps: Developer pushes, GitHub merges, Jenkins builds backend and frontend images, pushes versioned tags to Docker Hub, Git manifests are updated, ArgoCD auto-syncs, Kubernetes rolls the update, and Prometheus/Grafana/Alertmanager observe everything. A gold return loop notes: rollback equals git revert.](images/diagram-pipeline.png)
*The entire delivery contract in one picture. CI never touches the cluster.*

Each service owns a declarative `Jenkinsfile` with a boringly consistent contract: log in to Docker Hub with stored credentials, run a multi-stage build, push `0.0.<BUILD_NUMBER>` and `:latest`. The frontend build injects the production API URL as a Docker build-arg, so the same Dockerfile works for local Compose and production.

Once the new image tag lands in the Kubernetes manifests… Jenkins' job is done. It has no `kubeconfig`. It cannot touch the cluster.

![Illustration: a glowing loop connecting a Git merge symbol, a Kubernetes ship's wheel, and a rocket carrying a shipping container, with a self-healing heartbeat pulsing at the center](images/gitops-loop.png)
*GitOps: the cluster continuously bends itself toward whatever Git says it should be.*

That's where **ArgoCD** takes over. It watches `deployment/k8s_manifest/`, diffs desired state against live state, and converges any drift automatically. The operational consequences are significant:

- **Deploys are pull requests.** Yeah, infrastructure changes get code review now.
- **Rollbacks are `git revert`.** The same audited workflow used to roll forward is used to roll back.
- **Drift dies fast.** Someone edits the cluster directly? ArgoCD flags it `OutOfSync` and heals it.

## If it isn't monitored, it isn't done

![Illustration: an engineer with a coffee mug sits before a dark mission-control wall of holographic Grafana-style dashboards — line charts, gauges, heatmaps — with a red alert bell glowing](images/observability.png)
*Sunday-morning energy, courtesy of Prometheus and Grafana.*

The final Ansible playbook drops in the battle-tested `kube-prometheus-stack` Helm chart: **Prometheus** scrapes cluster and node metrics, **Grafana** renders the pre-provisioned Kubernetes dashboards, and **Alertmanager** routes the pager-worthy stuff. Each UI gets its own ingress and its own Terraform-created DNS record, proxied behind Cloudflare — so the origin stays hidden and TLS is terminated at the edge.

The app earns its keep too: the backend refuses traffic until both MongoDB *and* Redis connections succeed (a failed dependency = clean non-zero exit that the orchestrator restarts), and the hottest read endpoints — the blog feed, featured and latest posts — are served through a **Redis read-through cache**, keeping MongoDB out of the blast radius of a traffic spike.

## The scoreboard

| Layer | Stack |
|---|---|
| App | React 18 · Vite · TypeScript · Tailwind · Express TS · Mongoose · Passport (Google OAuth) · bcrypt |
| Data | MongoDB 7 (stateful) · Redis 7 (read-through cache) |
| Containers | Multi-stage Dockerfiles, non-root runtime, images → Docker Hub |
| Infra | Terraform (AWS + Cloudflare + tls) · encrypted S3 state |
| Config | Ansible — 6 idempotent playbooks |
| Platform | Kubernetes (kind on EC2) · NGINX Ingress · ArgoCD GitOps |
| CI | Jenkins declarative pipelines per service |
| Observability | Prometheus · Grafana · Alertmanager |
| Quality | Jest + Supertest · Vitest · Husky · lint-staged |

## Three lessons that hurt a little

1. **Provisioners are glue, not architecture.** Terraform provisioners made `apply` magical, but they fight drift correction. The fix wasn't fewer provisioners — it was making every Ansible playbook idempotent, so being re-run is boring.
2. **Kind on EC2 is a feature, not a compromise.** A fully standard Kubernetes cluster with zero control-plane cost, and the manifests deploy untouched onto EKS the day I need managed scale. Design for portability, buy managed later.
3. **The CI/CD trust boundary is worth the extra moving part.** Giving Jenkins a kubeconfig would have deleted a hundred lines of YAML — and created a standing credential I never wanted on the internet. ArgoCD's pull model means there is nothing to steal on the CI box.

## What's next

EKS in the existing private subnets, Horizontal Pod Autoscalers, cert-manager TLS, Trivy image scanning in the pipelines, and tighter security groups (SSH only from the Jenkins SG). The roadmap lives in the repo — GitOps means even my TODOs are versioned.

## Steal this project

The whole thing — application, Terraform, Ansible, manifests, pipelines, and a full project documentation file — is open source:

👉 **GitHub: [Spygram/wanderlust](https://github.com/Spygram/wanderlust)** — live endpoints for the frontend, API, ArgoCD, and Grafana are listed in the docs.

If this saved you an idea (or an argument with a Jenkinsfile), drop a ⭐ on the repo, and tell me in the comments: **what's the one manual step in your pipeline you haven't dared to automate yet?**

*Happy shipping — may your clusters always converge.* 🚀