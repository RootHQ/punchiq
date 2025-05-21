# Punch IQ - Serverless Time Tracking System

This project implements a modern, serverless employee punch system using:

- **Frontend:** Angular + S3 + CloudFront
- **Backend:** FastAPI (Python) on AWS Lambda
- **Infraestructura:** Terraform
- **Base de datos:** DynamoDB
- **Mensajería:** Amazon SQS

## 📁 Estructura del Proyecto

```
punch-iq-project/
├── frontend/         # Angular frontend
├── backend/          # FastAPI and worker Lambdas
├── infra/            # Terraform infrastructure code
```

## 🚀 Cómo desplegar

1. **Frontend**
   - Ir a `frontend/`
   - Ejecutar `npm install` y `ng build --configuration production`
   - Subir a S3: `aws s3 sync ./dist/punch-iq-frontend s3://<bucket> --delete`

2. **Backend**
   - Empaquetar `main.py` y `worker.py` como ZIP
   - Configurar las rutas en Terraform o subir manualmente

3. **Infraestructura**
   - Ir a `infra/`
   - Ejecutar `terraform init && terraform apply`

4. **Verificar**
   - API Gateway expuesto
   - Lambda funcionando
   - Logs en DynamoDB
   - Frontend público vía CloudFront

## 🧠 Autor
Este proyecto fue generado automáticamente por asistencia AI en colaboración con el equipo técnico.

---

Happy shipping 🚀
