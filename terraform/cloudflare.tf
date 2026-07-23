resource "cloudflare_dns_record" "api_dns_record" {
  zone_id = var.cloudflare_zone_id
  name    = "backend.sujandongol.com.np"
  ttl     = 1
  type    = "A"
  content = aws_instance.deployment-server.public_ip
  proxied = true
}
resource "cloudflare_dns_record" "frontend_dns_record" {
  zone_id = var.cloudflare_zone_id
  name    = "frontend.sujandongol.com.np"
  ttl     = 1
  type    = "A"
  content = aws_instance.deployment-server.public_ip
  proxied = true
}

resource "cloudflare_dns_record" "argocd_dns_record" {
  zone_id = var.cloudflare_zone_id
  name    = "argocd.sujandongol.com.np"
  ttl     = 1
  type    = "A"
  content = aws_instance.deployment-server.public_ip
  proxied = true
}