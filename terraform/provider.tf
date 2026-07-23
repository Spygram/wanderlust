terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.47.0"
    }

    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }

    tls = {
      source  = "hashicorp/tls"
      version = "4.3.0"
    }

    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "5.17.0"
    }
  }

  backend "s3" {
    bucket  = "3-tier-project-statefile"
    key     = "vpc/terraform.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}

# provider "cloudflare" {
#   api_token = "Get_it_from_Cloudflare_account"
# }


provider "aws" {
  # Configuration options
  region = var.aws_region
}
