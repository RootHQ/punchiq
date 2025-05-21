# ⏱️ Cloud-Based Time Tracking System

A modern, serverless employee time tracking solution that enables employees to punch in/out, track break times, and synchronize data with NetSuite. Built with Angular, Python (FastAPI), and fully deployed on AWS using Lambda, S3, API Gateway, DynamoDB, and SQS.

---

## 🌐 Live Architecture Overview

![Architecture Diagram]
---

## 🧰 Tech Stack

| Layer        | Technology                    |
|--------------|-------------------------------|
| Frontend     | Angular 16+, hosted on S3 + CloudFront |
| Backend      | FastAPI + Python (AWS Lambda) |
| API Gateway  | Amazon API Gateway            |
| Database     | Amazon DynamoDB               |
| Messaging    | Amazon SQS                    |
| External API | NetSuite Integration          |
| CI/CD        | GitHub Actions                |
| IaC          | Terraform                     |
| Monitoring   | CloudWatch                    |
| DNS/Domain   | Amazon Route 53               |

---

## ✨ Features

- 🔐 Employee login using ID and secure PIN
- 🕑 Punch in/out and break logging
- 🔁 Sync punches to NetSuite (via SQS + Lambda Worker)
- 📝 Punch history and session status tracking
- 📱 Mobile and tablet responsive UI
- 📡 Serverless architecture with AWS
- ☁️ Infrastructure as Code with Terraform
- 🔁 Full CI/CD using GitHub Actions

---

## 📦 Project Structure

```bash
.
├── frontend/                   # Angular app (S3 hosted)
├── backend/                    # FastAPI app (Lambda functions)
│   ├── main.py                 # FastAPI entrypoint
│   ├── routers/                # API route modules
│   └── services/               # Business logic
│   └── lambdas/ 
├── terraform/                  # Infrastructure as Code
├── .github/workflows/          # GitHub Actions workflows
├── docs/                       # Architecture diagrams, ERDs
├── README.md                   # This file
