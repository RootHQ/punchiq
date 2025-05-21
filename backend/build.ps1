# Nombre de la layer y carpeta
$layerName = "jwt-layer"
$pythonFolder = "$layerName\python"

# Crear estructura de carpetas
Write-Host "Creando carpetas..."
New-Item -ItemType Directory -Force -Path $pythonFolder | Out-Null

# Instalar PyJWT dentro de la carpeta python/
Write-Host "Instalando PyJWT en $pythonFolder ..."
pip install PyJWT -t $pythonFolder

# Crear el archivo zip
$zipPath = "$PWD\$layerName.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath }

Write-Host "Comprimiendo layer en: $zipPath ..."
Compress-Archive -Path "$layerName\*" -DestinationPath $zipPath

Write-Host "Layer empaquetada exitosamente en: $zipPath"
Write-Host "Ahora puedes subir este archivo ZIP a AWS Lambda > Layers"
