# Configuración
$bucket = "punchiq-frontend-bucket"
$profile = "apiuserdeploy"
$source = "dist/frontend-web/browser"

Write-Host ">>> Ejecutando build de Angular..."
ng build --configuration production

Write-Host ">>> Eliminando TODOS los archivos anteriores del bucket..."
aws s3 rm "s3://$bucket" --recursive --profile $profile

Write-Host ">>> Subiendo archivos .js con el MIME correcto (application/javascript)..."

# Paso 1: eliminar archivos .js del bucket (si existen)
$jsFiles = Get-ChildItem -Path "$source" -Filter *.js -Recurse
foreach ($file in $jsFiles) {
    $relativePath = $file.FullName.Substring($source.Length + 1).Replace("\", "/")
    $s3Key = "s3://$bucket/$relativePath"
    Write-Host "  - Eliminando $s3Key"
    aws s3 rm $s3Key --profile $profile
}

# Paso 2: subir .js con MIME correcto
aws s3 cp "$source" "s3://$bucket" --recursive --exclude "*" --include "*.js" --content-type "application/javascript" --profile $profile

Write-Host ">>> Subiendo los demás archivos..."
aws s3 sync "$source" "s3://$bucket" --exclude "*.js" --delete --profile $profile

Write-Host ""
Write-Host ">>> ✅ Despliegue completo sin errores de MIME type."
Write-Host ">>> ℹ️ Asegúrate de tener habilitado 'Static Website Hosting' en S3:"
Write-Host "    - Index document: index.html"
Write-Host "    - Error document: index.html"
