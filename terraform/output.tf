output "instance_public_ip" {
  value       = aws_instance.jenkins_server.public_ip
  description = "public ip of jenkins server"
}

output "instance_public_ip" {
  value       = aws_instance.deployment-server.public_ip
  description = "public ip of deployment server"
}

resource "local_file" "ansible_inventory" {
  content  = <<EOT
[vm]
${aws_instance.deployment-server.public_ip}
EOT
  filename = "${path.module}/../deployment/ansible/inventory/inventory.ini"
}

