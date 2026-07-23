output "instance_public_ip" {
  value       = aws_instance.jenkins_server.public_ip
  description = "public ip of jenkins server"
}