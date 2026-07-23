# SSH Key Pair Generation
resource "tls_private_key" "vm_key" { algorithm = "ED25519" }

resource "aws_key_pair" "deployer_key" {
  key_name   = "wanderlust-key"
  public_key = tls_private_key.vm_key.public_key_openssh
}

resource "local_file" "private_key_pem" {
  content         = tls_private_key.vm_key.private_key_openssh
  filename        = "${path.module}/../wanderlust-key.pem"
  file_permission = "0600"
}

# Security Groups
resource "aws_security_group" "jenkins_sg" {
  name   = "wanderlust-jenkins-sg"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# resource "aws_security_group" "kind_cluster_sg" {
#   name   = "wanderlust-kind-cluster-sg"
#   vpc_id = aws_vpc.main.id

#   ingress {
#     from_port       = 22
#     to_port         = 22
#     protocol        = "tcp"
#     security_groups = [aws_security_group.jenkins_sg.id]
#   }
#   ingress {
#     from_port   = 80
#     to_port     = 80
#     protocol    = "tcp"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
#   ingress {
#     from_port   = 3000
#     to_port     = 3000
#     protocol    = "tcp"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
# }

# Public VM with Jenkins Remote Provisioner
resource "aws_instance" "jenkins_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public_subnet.id
  vpc_security_group_ids = [aws_security_group.jenkins_sg.id]
  key_name               = aws_key_pair.deployer_key.key_name
  iam_instance_profile   = data.aws_iam_instance_profile.labInstanceProfile.name

  root_block_device {
    volume_size           = 40
    volume_type           = "gp3"
    delete_on_termination = true
  }

  tags = { Name = "wanderlust-jenkins-server" }

  user_data = file("${path.module}/install_jenkins_docker.sh")

  user_data_replace_on_change = true
  
}

# resource "aws_instance" "kind_cluster" {
#   ami                    = data.aws_ami.ubuntu.id
#   instance_type          = "t2.large"
#   subnet_id              = aws_subnet.public_subnet.id
#   vpc_security_group_ids = [aws_security_group.kind_cluster_sg.id]
#   key_name               = aws_key_pair.deployer_key.key_name
#   iam_instance_profile   = data.aws_iam_instance_profile.labInstanceProfile.name

#   root_block_device {
#     volume_size           = 32
#     volume_type           = "gp3"
#     delete_on_termination = true
#   }

#   tags = { Name = "wanderlust-kind-cluster" }

#   user_data = file("${path.module}/install_docker_kind.sh")

#   user_data_replace_on_change = true


# }


