#!/usr/bin/env python3
"""Render Wanderlust architecture + CI/CD pipeline diagrams for the Medium article."""
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
def F(size, bold=True):
    return ImageFont.truetype(FONT_DIR + ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)

# Palette (matches the generated illustrations)
BG        = (11, 18, 32)      # deep navy
CLUSTER   = (17, 26, 46)      # cluster fill
CLUSTER_B = (51, 71, 105)     # cluster border
WHITE     = (248, 250, 252)
GREY      = (148, 163, 184)
CYAN      = (56, 189, 248)
ORANGE    = (251, 146, 60)
GOLD      = (250, 204, 21)
GREEN     = (52, 211, 153)
VIOLET    = (167, 139, 250)
RED       = (248, 113, 113)
PINK      = (244, 114, 182)
BOX_FILL  = (30, 41, 66)

def rrect(d, box, fill, border, r=22, bw=5):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=border, width=bw)

def label(d, cx, cy, text, font, color=WHITE):
    bb = d.textbbox((0, 0), text, font=font)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    d.text((cx - w / 2, cy - h / 2), text, font=font, fill=color)

def box_with_text(d, box, border, title, subs, tcolor=None, fill=BOX_FILL, lh=34, gap=10):
    rrect(d, box, fill, border)
    x1, y1, x2, y2 = box
    cx = (x1 + x2) / 2
    lines = [(title, F(30), tcolor or border)] + [(s, F(22, False), GREY) for s in subs]
    total = len(lines) * lh + (len(lines) - 1) * gap
    y = (y1 + y2) / 2 - total / 2 + lh / 2
    for text, font, color in lines:
        label(d, cx, y, text, font, color)
        y += lh + gap

def wrap_px(d, text, font, max_w):
    """Wrap text into lines that fit max_w pixels."""
    lines, cur = [], ""
    for w_ in text.split():
        trial = (cur + " " + w_).strip()
        if d.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur: lines.append(cur)
            cur = w_
    if cur: lines.append(cur)
    return lines

def arrow(d, p1, p2, color, width=6, dashed=False, head=18):
    x1, y1 = p1; x2, y2 = p2
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    # trim line so head doesn't overshoot target box edge
    ex, ey = x2 - head * math.cos(ang), y2 - head * math.sin(ang)
    if dashed:
        segs = 18
        for i in range(0, segs, 2):
            t1, t2 = i / segs, (i + 1) / segs
            d.line((x1 + (ex - x1) * t1, y1 + (ey - y1) * t1,
                    x1 + (ex - x1) * t2, y1 + (ey - y1) * t2), fill=color, width=width)
    else:
        d.line((x1, y1, ex, ey), fill=color, width=width)
    d.polygon([(x2, y2),
               (x2 - head * math.cos(ang - 0.42), y2 - head * math.sin(ang - 0.42)),
               (x2 - head * math.cos(ang + 0.42), y2 - head * math.sin(ang + 0.42))],
              fill=color)

def elbow_arrow(d, x1, y1, x2, y2, midx, color, width=6, dashed=False):
    arrow(d, (midx, y1), (midx, y2 + (-18 if y2 < y1 else 18)), color, 0 if dashed else 0)
    # horizontal then vertical
    d.line((x1, y1, midx, y1), fill=color, width=width)
    arrow(d, (midx, y1), (x2 if midx != x2 else midx, y2), color, width, dashed) if midx == x2 else None

# =========================================================================
# Diagram 1 — Architecture
# =========================================================================
W, H = 2300, 1640
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

label(d, W / 2, 55, "WANDERLUST — PRODUCTION ARCHITECTURE ON AWS", F(40), WHITE)
label(d, W / 2, 100, "terraform apply  →  ansible bootstrap  →  gitops self-healing cluster", F(26, False), GREY)

# Users
box_with_text(d, (900, 150, 1400, 240), CYAN, "Internet Users", ["HTTPS"])
# Cloudflare
box_with_text(d, (820, 300, 1380, 395), ORANGE, "Cloudflare DNS + Edge Proxy",
              ["A-records created by Terraform"])

# VPC cluster
vpc = (90, 480, 2210, 1560)
rrect(d, vpc, CLUSTER, CLUSTER_B, r=34, bw=6)
label(d, 1150, 525, "AWS VPC 10.0.0.0/16  ·  public subnet  ·  us-east-1  ·  state in encrypted S3",
      F(26, False), GREY)

# Jenkins box
box_with_text(d, (150, 590, 800, 820), VIOLET, "EC2 — jenkins-server",
              ["Jenkins CI pipelines", "multi-stage Docker builds", "push images to Docker Hub"])
# Terraform note box
box_with_text(d, (150, 950, 800, 1220), GOLD, "Bootstrap (zero-touch)",
               ["1. terraform apply", "2. wait-for-SSH provisioner", "3. 6 Ansible playbooks:", "   tools → kind cluster → ingress", "   → mongo seed → ArgoCD → monitoring"])

# Deployment cluster
dep = (880, 580, 2150, 1500)
rrect(d, dep, (15, 26, 50), GREEN, r=30, bw=6)
label(d, 1515, 625, "EC2 — deployment-server  ·  Kubernetes cluster (kind)", F(26), GREEN)

# Ingress
box_with_text(d, (940, 670, 2090, 780), CYAN, "NGINX Ingress Controller",
              ["host-based routing: frontend.* · backend.* · argocd.* · grafana.*"])

# Row 2
box_with_text(d, (940, 850, 1310, 1035), PINK, "Frontend", ["Nginx serving", "React 18 SPA", "TS + Tailwind"], lh=30, gap=6)
box_with_text(d, (1370, 850, 1740, 1035), ORANGE, "Backend API", ["Express + TypeScript", "JWT cookie auth + RBAC", "Google OAuth"], lh=30, gap=6)
box_with_text(d, (1800, 850, 2090, 1035), VIOLET, "ArgoCD", ["GitOps sync", "auto self-heal"], lh=30, gap=6)

# Row 3
box_with_text(d, (940, 1105, 1310, 1265), GREEN, "MongoDB", ["stateful workload", "posts + users"], lh=28, gap=6)
box_with_text(d, (1370, 1105, 1740, 1265), RED, "Redis", ["read-through cache", "feed endpoints"], lh=28, gap=6)
box_with_text(d, (1800, 1105, 2090, 1265), GOLD, "Monitoring", ["Prometheus", "Grafana · Alerts"], lh=28, gap=6)

# Git manifests note
box_with_text(d, (940, 1335, 2090, 1455), CYAN, "Git = single source of truth",
              ["deployment/k8s_manifest — desired state watched by ArgoCD"], lh=28, gap=8)

# Arrows
arrow(d, (1150, 240), (1150, 300), CYAN)                       # users -> cloudflare
arrow(d, (1150, 395), (1150, 660), ORANGE)                     # cloudflare -> ingress (through vpc)
arrow(d, (960, 780), (1080, 850), CYAN)                        # ingress -> frontend
arrow(d, (2070, 780), (1620, 850), CYAN)                       # ingress -> backend (from right side)
arrow(d, (1440, 1035), (1150, 1105), ORANGE)                   # backend -> mongo
arrow(d, (1555, 1035), (1555, 1105), ORANGE)                   # backend -> redis
arrow(d, (480, 820), (480, 950), GOLD)                         # jenkins/boot note connector
arrow(d, (1950, 1035), (1950, 1105), VIOLET, dashed=True)      # argocd -> monitoring
arrow(d, (1515, 1265), (1515, 1335), CYAN, dashed=True)        # manifests sync from git
arrow(d, (800, 705), (880, 780), VIOLET, dashed=True)          # jenkins -> k8s (via images)

# Docker Hub box outside, right of VPC? place left bottom inside margin
img.save("medium/images/diagram-architecture.png")
print("architecture saved")

# =========================================================================
# Diagram 2 — CI/CD GitOps pipeline
# =========================================================================
W2, H2 = 2640, 860
img2 = Image.new("RGB", (W2, H2), BG)
d = ImageDraw.Draw(img2)

label(d, W2 / 2, 60, "COMMIT → IMAGE → CLUSTER : THE GITOPS PIPELINE", F(40), WHITE)
label(d, W2 / 2, 108, "Jenkins builds immutable artifacts — ArgoCD continuously reconciles the cluster with Git", F(25, False), GREY)

steps = [
    ("1", "Developer", "git push / pull request", CYAN),
    ("2", "GitHub", "merge to main + PR checks", GREEN),
    ("3", "Jenkins (EC2)", "webhook triggers CI · docker build backend + frontend", VIOLET),
    ("4", "Docker Hub", "tag 0.0.<BUILD#> + :latest", ORANGE),
    ("5", "Git Manifests", "k8s desired state updated in repo", GOLD),
    ("6", "ArgoCD", "detects drift → auto-sync · self-heal", PINK),
    ("7", "Kubernetes", "rolling update of backend & frontend", GREEN),
    ("8", "Observability", "Prometheus · Grafana · Alertmanager", RED),
]
x = 60
bw, gap = 290, 22
for num, title, sub, col in steps:
    x1 = x; x2 = x + bw
    rrect(d, (x1, 210, x2, 480), BOX_FILL, col)
    d.ellipse((x1 + bw / 2 - 30, 235, x1 + bw / 2 + 30, 295), fill=col)
    label(d, x1 + bw / 2, 265, num, F(30), BG)
    label(d, x1 + bw / 2, 345, title, F(25), col)
    sub_lines = wrap_px(d, sub, F(19, False), bw - 36)[:3]
    yy = 395
    for sl in sub_lines:
        label(d, x1 + bw / 2, yy, sl, F(19, False), GREY)
        yy += 27
    if num != "8":
        arrow(d, (x2 + 2, 345), (x2 + gap - 2, 345), WHITE, width=5, head=14)
    x += bw + gap

# feedback dashed loop: ArgoCD back to Git manifests ("Git remains source of truth")
y_loop = 580
d.line((60 + (bw + gap) * 4 + bw / 2, 480, 60 + (bw + gap) * 4 + bw / 2, y_loop), fill=GOLD, width=4)
d.line((60 + (bw + gap) * 5 + bw / 2, 480, 60 + (bw + gap) * 5 + bw / 2, y_loop), fill=GOLD, width=4)
for xx in [60 + (bw + gap) * 4 + bw / 2]:
    pass
d.line((60 + (bw + gap) * 4 + bw / 2, y_loop, 60 + (bw + gap) * 5 + bw / 2, y_loop), fill=GOLD, width=4)
label(d, 60 + (bw + gap) * 4.5 + bw / 2, y_loop + 45, "rollback = git revert · audit trail for every change", F(24, False), GOLD)

# legend strip
label(d, W2 / 2, 720, "CI needs zero cluster credentials — deploy rights live only inside the cluster (ArgoCD)",
      F(28), CYAN)
img2.save("medium/images/diagram-pipeline.png")
print("pipeline saved")
