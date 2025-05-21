# Punch IQ - Frontend (Angular)

This Angular frontend is part of the Punch IQ project.

## 📦 Features

- Employee login interface
- Punch In / Punch Out functionality
- Log viewer for punch history
- Responsive design with basic CSS

## 🚀 Build and Deploy

### Build for production

```bash
ng build --configuration production
```

### Deploy to S3

```bash
aws s3 sync ./dist/punch-iq-frontend s3://my-app-frontend-bucket --delete
```

Ensure your S3 bucket is configured as a static website.

## 🧠 Notes

- Make sure API Gateway endpoint is configured correctly in `punch.service.ts`.
- Use environment variables or proxy config for cleaner development.
