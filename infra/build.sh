#!/bin/bash

# Configuraciones
BUCKET_NAME="punchiq-frontend-bucket"
DIST_FOLDER="dist/punch-iq-frontend"

echo "📦 1. Construyendo Angular..."
cd ../frontend
ng build --configuration production --output-path=../infra/$DIST_FOLDER
cd ../infra
if [ $? -ne 0 ]; then
  echo "❌ Error en la construcción de Angular. Abortando."
  exit 1
fi
echo "✅ Construcción de Angular completada."
echo "🚀 2. Desplegando en S3..."

echo "⬆️ 2. Sincronizando archivos con S3..." 
aws s3 sync $DIST_FOLDER s3://$BUCKET_NAME --delete --profile apiuserdeploy

echo "🛠️ 3. Corrigiendo tipos MIME en S3..."

# Archivos JS
find $DIST_FOLDER -name "*.js" | while read file; do
  key=$(echo "$file" | sed "s|$DIST_FOLDER/||")
  aws s3 cp "$file" "s3://$BUCKET_NAME/$key" --content-type "application/javascript" --acl public-read
done

# Archivos CSS
find $DIST_FOLDER -name "*.css" | while read file; do
  key=$(echo "$file" | sed "s|$DIST_FOLDER/||")
  aws s3 cp "$file" "s3://$BUCKET_NAME/$key" --content-type "text/css" --acl public-read
done

# Favicon
if [ -f "$DIST_FOLDER/favicon.ico" ]; then
  aws s3 cp "$DIST_FOLDER/favicon.ico" "s3://$BUCKET_NAME/favicon.ico" --content-type "image/x-icon" --acl public-read
fi

echo "✅ Despliegue completado con éxito. Puedes acceder a:"
echo "🌐 http://$BUCKET_NAME.s3-website-us-east-1.amazonaws.com"
