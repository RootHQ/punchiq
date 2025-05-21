# Terraform Infrastructure - Punch IQ

This folder contains the Terraform configuration to provision all necessary AWS resources for the Punch IQ application.

## 🧱 Provisioned Resources

- AWS Lambda (FastAPI handler)
- AWS Lambda (Worker)
- Amazon API Gateway (HTTP)
- Amazon SQS Queue
- DynamoDB Tables:
  - logs
  - employee
  - setting
- S3 Bucket for Frontend Hosting
- IAM Roles for Lambda Execution

## 🚀 Deployment

To deploy the infrastructure:

```bash
cd infra
chmod +x build.sh
./build.sh
```

Make sure you have Terraform and AWS CLI configured with access to your AWS account.

