provider "aws" {
  region = "us-east-1"
}

##########################
# S3 Bucket for Frontend
##########################
resource "aws_s3_bucket" "frontend" {
  bucket = "punchiq-frontend-bucket"
}

resource "aws_s3_bucket_website_configuration" "frontend_website" {
  bucket = aws_s3_bucket.frontend.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

resource "aws_s3_bucket_policy" "frontend_policy" {
  bucket = aws_s3_bucket.frontend.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Principal = "*",
        Action    = ["s3:GetObject"],
        Resource  = ["${aws_s3_bucket.frontend.arn}/*"]
      }
    ]
  })
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket                  = aws_s3_bucket.frontend.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

##########################
# IAM Policy for Access
##########################
resource "aws_iam_policy" "punchiq_full_access" {
  name        = "PunchIQFullAccess"
  description = "Permite gestionar recursos de PunchIQ"
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:CreateBucket",
          "s3:PutBucketPolicy",
          "s3:GetBucketWebsite",
          "s3:PutBucketWebsite",
          "s3:GetObject",
          "s3:ListBucket"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "dynamodb:CreateTable",
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Scan",
          "dynamodb:DescribeTable"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "iam:CreateRole",
          "iam:AttachRolePolicy",
          "iam:PassRole",
          "iam:CreatePolicy"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "lambda:CreateFunction",
          "lambda:UpdateFunctionCode",
          "lambda:InvokeFunction"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "apigateway:POST",
          "apigateway:GET",
          "apigateway:PUT",
          "apigateway:DELETE"
        ],
        Resource = "*"
      }
    ]
  })
}

##########################
# IAM Group for Deployment
##########################
resource "aws_iam_group" "deploy_group" {
  name = "DeployGroup"
}

resource "aws_iam_user_group_membership" "apiuser_group_membership" {
  user = "ApiUserDeploy"
  groups = [aws_iam_group.deploy_group.name]
}

resource "aws_iam_group_policy_attachment" "group_policy_attachment" {
  group      = aws_iam_group.deploy_group.name
  policy_arn = aws_iam_policy.punchiq_full_access.arn
}

##########################
# Outputs
##########################
output "frontend_bucket_url" {
  value       = "http://${aws_s3_bucket.frontend.bucket}.s3-website-${var.aws_region}.amazonaws.com"
  description = "URL pública del frontend Angular"
}

variable "aws_region" {
  description = "Región AWS"
  default     = "us-east-1"
}
