# Makefile for Punch IQ Project

.PHONY: deploy zip-lambdas build-frontend

zip-lambdas:
	zip -j lambda_fastapi.zip backend/lambda/main.py
	zip -j lambda_worker.zip backend/lambda/worker.py

deploy: zip-lambdas
	cd infra && terraform init && terraform apply -auto-approve

build-frontend:
	cd frontend && npm install && npm run build -- --configuration production

deploy-frontend:
	aws s3 sync frontend/dist/punch-iq-frontend s3://my-app-frontend-bucket --delete
