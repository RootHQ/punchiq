# Configuraciones
$BucketName = "punchiq-frontend-bucket"
$DistFolder = "..\frontend\dist\punch-iq-frontend"
$LambdaFolder = "..\backend\lambda"
$LambdaZip = "lambda.zip"

Write-Host "`n📦 1. Construyendo Angular..."
Set-Location ..\frontend
ng build --configuration production

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error en la construcción de Angular. Abortando." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Construcción de Angular completada." -ForegroundColor Green
Set-Location ..\infra

Write-Host "`n🚀 2. Limpiando Bucket S3..."
aws s3 rm "s3://$BucketName" --recursive --profile apiuserdeploy

Write-Host "`n⬆️ 3. Subiendo archivos a S3..."
aws s3 sync $DistFolder "s3://$BucketName" --delete --profile apiuserdeploy

Write-Host "`n🛠️ 4. Corrigiendo tipos MIME..."

# HTML
Get-ChildItem "$DistFolder\*.html" -Recurse | ForEach-Object {
    $key = $_.FullName.Replace("$DistFolder\", "").Replace("\", "/")
    aws s3 cp $_.FullName "s3://$BucketName/$key" --content-type "text/html" --profile apiuserdeploy
}

# JS
Get-ChildItem "$DistFolder\*.js" -Recurse | ForEach-Object {
    $key = $_.FullName.Replace("$DistFolder\", "").Replace("\", "/")
    aws s3 cp $_.FullName "s3://$BucketName/$key" --content-type "application/javascript" --profile apiuserdeploy
}

# CSS
Get-ChildItem "$DistFolder\*.css" -Recurse | ForEach-Object {
    $key = $_.FullName.Replace("$DistFolder\", "").Replace("\", "/")
    aws s3 cp $_.FullName "s3://$BucketName/$key" --content-type "text/css" --profile apiuserdeploy
}

# Favicon
$Favicon = "$DistFolder\favicon.ico"
if (Test-Path $Favicon) {
    aws s3 cp $Favicon "s3://$BucketName/favicon.ico" --content-type "image/x-icon" --profile apiuserdeploy
}

Write-Host "`n✅ Archivos subidos y tipos MIME corregidos."

Write-Host "`n📦 5. Empaquetando Lambda..."
Compress-Archive -Path "$LambdaFolder\*" -DestinationPath ".\$LambdaZip" -Force

Write-Host "`n🚀 6. Ejecutando Terraform..."
terraform init
terraform apply -auto-approve

Write-Host "`n✅ Despliegue completo:"
Write-Host "🌐 http://$BucketName.s3-website-us-east-1.amazonaws.com" -ForegroundColor Cyan
